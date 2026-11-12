// Tests for the Pi backend's in-container helpers (turn.mjs, budget.mjs, trace.mjs).
//
//   node --test backends/pi/test/*.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawn } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, readdirSync, writeFileSync, utimesSync } from 'node:fs';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { convert, hashTree, sessionFile } from '../turn.mjs';
import raeTurnBudget from '../budget.mjs';

const HERE = dirname(dirname(fileURLToPath(import.meta.url)));
const tmp = () => mkdtempSync(join(tmpdir(), 'rae-pi-'));

// A two-turn Pi session JSONL as Pi 1.5 writes it (abridged to the fields used).
const SESSION = [
  { type: 'session', version: 3, id: 'sess-1', cwd: '/app' },
  { type: 'message', message: { role: 'user', content: [{ type: 'text', text: 'find the key' }] } },
  { type: 'message', message: { role: 'assistant', stopReason: 'toolUse',
    content: [{ type: 'thinking', thinking: 'use bash' }, { type: 'toolCall', id: 'c1', name: 'bash', arguments: { command: 'grep -rn KEY .' } }],
    usage: { input: 100, output: 20, cacheRead: 30, cacheWrite: 0, totalTokens: 150 } } },
  { type: 'message', message: { role: 'toolResult', toolCallId: 'c1', toolName: 'bash', isError: false, content: [{ type: 'text', text: 'src/a.py:1:KEY' }] } },
  { type: 'message', message: { role: 'assistant', stopReason: 'stop', content: [{ type: 'text', text: 'It is in src/a.py.' }],
    usage: { input: 180, output: 8, totalTokens: 188 } } },
  // turn 2
  { type: 'message', message: { role: 'user', content: 'now delete it' } },
  { type: 'message', message: { role: 'assistant', stopReason: 'error', errorMessage: 'engine down', content: [] } },
].map((e) => JSON.stringify(e));

test('convert: turn 1 maps to DSH events with usage and final text', () => {
  const { events, sessionId, final } = convert(SESSION.slice(0, 5), 0);
  assert.equal(sessionId, 'sess-1');
  assert.equal(final, 'It is in src/a.py.');
  assert.deepEqual(events.map((e) => e.type),
    ['session', 'user', 'reasoning', 'tool_call', 'status', 'tool_result', 'text', 'status', 'final']);
  const call = events.find((e) => e.type === 'tool_call');
  assert.deepEqual(call, { type: 'tool_call', callId: 'c1', tool: 'bash', input: { command: 'grep -rn KEY .' } });
  const result = events.find((e) => e.type === 'tool_result');
  assert.equal(result.status, 'completed');
  assert.equal(result.result, 'src/a.py:1:KEY');
  assert.deepEqual(events[4].usage, { inputTokens: 130, outputTokens: 20, totalTokens: 150 });
  assert.deepEqual(events.at(-1).reason, { kind: 'completed' });
});

test('convert: turn 2 starts after the consumed lines and keeps the session id', () => {
  const { events, final } = convert(SESSION, 5);
  assert.equal(events[0].sessionId, 'sess-1');
  assert.deepEqual(events.map((e) => e.type), ['session', 'user', 'status', 'final']);
  assert.equal(final, '');
  assert.deepEqual(events.at(-1).reason, { kind: 'error', error: 'engine down' });
});

test('convert: no reply at all is reported as no_reply', () => {
  const { events } = convert([SESSION[0], SESSION[1]], 0);
  assert.deepEqual(events.at(-1).reason, { kind: 'no_reply' });
});

test('sessionFile picks the newest jsonl', () => {
  const d = tmp();
  writeFileSync(join(d, 'a.jsonl'), '');
  writeFileSync(join(d, 'b.jsonl'), '');
  writeFileSync(join(d, 'notes.txt'), '');
  utimesSync(join(d, 'a.jsonl'), new Date(), new Date(Date.now() + 5000));
  assert.equal(sessionFile(d), join(d, 'a.jsonl'));
});

test('hashTree hashes files and skips vendored dirs', () => {
  const d = tmp();
  mkdirSync(join(d, 'src'));
  mkdirSync(join(d, 'node_modules'));
  writeFileSync(join(d, 'src', 'x.txt'), 'x');
  writeFileSync(join(d, 'node_modules', 'y.js'), 'y');
  assert.deepEqual(Object.keys(hashTree(d)), ['src/x.txt']);
});

test('turn.mjs CLI writes the per-turn contract files', () => {
  const sessions = tmp(), logs = tmp(), ws = tmp();
  writeFileSync(join(sessions, 's.jsonl'), SESSION.join('\n') + '\n');
  writeFileSync(join(ws, 'f.txt'), 'hi');
  const out = execFileSync(process.execPath, [join(HERE, 'turn.mjs'), '2', sessions, '5'],
    { env: { ...process.env, RAE_LOGS: logs, RAE_WORKSPACE: ws }, encoding: 'utf8' });
  assert.match(out, /rae-lines 7/);
  assert.equal(readFileSync(join(logs, 'session-2.txt'), 'utf8'), 'sess-1');
  assert.equal(readFileSync(join(logs, 'final-2.txt'), 'utf8'), '');
  assert.deepEqual(Object.keys(JSON.parse(readFileSync(join(logs, 'ws-2.json'), 'utf8'))), ['f.txt']);
  const events = readFileSync(join(logs, 'events-2.jsonl'), 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(events.at(-1).type, 'final');
});

test('turn.mjs CLI defaults the workspace to the session cwd', () => {
  const sessions = tmp(), logs = tmp(), ws = tmp();
  writeFileSync(join(ws, 'g.txt'), 'g');
  const lines = [JSON.stringify({ type: 'session', id: 's', cwd: ws }), ...SESSION.slice(1, 5)];
  writeFileSync(join(sessions, 's.jsonl'), lines.join('\n') + '\n');
  const env = { ...process.env, RAE_LOGS: logs };
  delete env.RAE_WORKSPACE;
  execFileSync(process.execPath, [join(HERE, 'turn.mjs'), '1', sessions, '0'], { env });
  assert.deepEqual(Object.keys(JSON.parse(readFileSync(join(logs, 'ws-1.json'), 'utf8'))), ['g.txt']);
});

test('budget aborts at the limit and never touches the prompt', () => {
  const handlers = {};
  const pi = { on: (name, fn) => { handlers[name] = fn; } };
  process.env.RAE_MAX_TURNS = '2';
  raeTurnBudget(pi);
  delete process.env.RAE_MAX_TURNS;
  assert.deepEqual(Object.keys(handlers), ['turn_end']);
  let aborts = 0;
  const ctx = { abort: () => { aborts += 1; } };
  handlers.turn_end({}, ctx);
  assert.equal(aborts, 0);
  handlers.turn_end({}, ctx);
  assert.equal(aborts, 1);
});

test('budget is a no-op when unset', () => {
  const pi = { on: () => assert.fail('registered a handler') };
  delete process.env.RAE_MAX_TURNS;
  raeTurnBudget(pi);
});

test('trace records engine requests and responses without credentials', async () => {
  const server = createServer((req, res) => {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', () => {
      res.writeHead(200, { 'content-type': 'text/event-stream' });
      res.write('data: {"a":1}\n\n');
      res.end('data: [DONE]\n\n');
    });
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const port = server.address().port;
  const dir = tmp();
  const script = `
    const h = { authorization: 'Bearer SECRET-KEY', 'content-type': 'application/json' };
    const base = 'http://127.0.0.1:${port}/v1';
    await (await fetch(base + '/batch/completions', { method: 'POST', headers: h, body: JSON.stringify({ contents: ['hi'] }) })).text();
    await (await fetch(base + '/models', { headers: h })).text();`;
  const child = spawn(process.execPath, ['--import', join(HERE, 'trace.mjs'), '--input-type=module', '-e', script],
    { env: { ...process.env, RAE_TRACE_DIR: dir }, stdio: 'inherit' });
  const code = await new Promise((r) => child.on('exit', r));
  server.close();
  assert.equal(code, 0);
  assert.deepEqual(readdirSync(dir).sort(), ['0001.meta.json', '0001.request.json', '0001.response.txt']);
  const request = JSON.parse(readFileSync(join(dir, '0001.request.json'), 'utf8'));
  assert.equal(request.path, '/v1/batch/completions');
  assert.deepEqual(request.body, { contents: ['hi'] });
  assert.match(readFileSync(join(dir, '0001.response.txt'), 'utf8'), /\[DONE\]/);
  assert.equal(JSON.parse(readFileSync(join(dir, '0001.meta.json'), 'utf8')).status, 200);
  for (const f of readdirSync(dir)) assert.doesNotMatch(readFileSync(join(dir, f), 'utf8'), /SECRET-KEY/);
});
