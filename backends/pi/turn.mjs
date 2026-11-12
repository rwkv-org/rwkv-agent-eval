// After user turn N of a Pi run: turn Pi's session log into the backend contract
// files that runner/ reads (README "框架接口"), in the same shape DSH writes them.
//
//   node /opt/rae-pi/turn.mjs <n> <session dir> <start line>
//
// Pi appends every turn of one conversation to a single session JSONL (resumed
// with --continue). Lines after <start line> belong to turn N. Writes:
//   /logs/agent/events-N.jsonl   DSH-schema events: session, text, reasoning,
//                                tool_call, tool_result, status (usage), final
//   /logs/agent/final-N.txt      last assistant text of the turn (may be empty)
//   /logs/agent/session-N.txt    Pi session id
//   /logs/agent/ws-N.json        sha256 of every file under the workspace
//                                (RAE_WORKSPACE, default: the session's cwd,
//                                i.e. the image WORKDIR Pi started in)
// Prints "rae-lines <total lines>" so the caller knows where turn N+1 starts.
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';

export function sessionFile(dir) {
  let best = null;
  for (const name of readdirSync(dir)) {
    if (!name.endsWith('.jsonl')) continue;
    const st = statSync(join(dir, name));
    if (!best || st.mtimeMs > best.mtimeMs || (st.mtimeMs === best.mtimeMs && name > best.name)) best = { name, mtimeMs: st.mtimeMs };
  }
  return best ? join(dir, best.name) : null;
}

function text(content) {
  if (typeof content === 'string') return content;
  if (!Array.isArray(content)) return '';
  return content.filter((b) => b && b.type === 'text' && typeof b.text === 'string').map((b) => b.text).join('');
}

// Pi stop reasons -> the `reason.kind` DSH puts on its final event.
const KIND = { stop: 'completed', toolUse: 'completed', length: 'max_tokens', aborted: 'aborted', error: 'error' };

/** Convert the session lines of one turn to DSH-schema events. */
export function convert(lines, startLine) {
  const events = [];
  let sessionId = '', cwd = '', lastText = '', lastStop = '', lastError = '';
  lines.forEach((line, index) => {
    let e;
    try { e = JSON.parse(line); } catch { return; }
    if (!e || typeof e !== 'object') return;
    if (e.type === 'session') { sessionId = e.id || sessionId; cwd = e.cwd || cwd; return; }
    if (index < startLine || e.type !== 'message' || !e.message) return;
    const m = e.message;
    if (m.role === 'assistant') {
      for (const b of Array.isArray(m.content) ? m.content : []) {
        if (b.type === 'thinking' && b.thinking) events.push({ type: 'reasoning', text: b.thinking });
        else if (b.type === 'text' && b.text) events.push({ type: 'text', text: b.text });
        else if (b.type === 'toolCall') events.push({ type: 'tool_call', callId: b.id, tool: b.name, input: b.arguments ?? {} });
      }
      const u = m.usage || {};
      const input = (u.input || 0) + (u.cacheRead || 0) + (u.cacheWrite || 0);
      events.push({ type: 'status', phase: 'step_end', stopReason: m.stopReason,
        usage: { inputTokens: input, outputTokens: u.output || 0, totalTokens: u.totalTokens || input + (u.output || 0) } });
      const t = text(m.content).trim();
      if (t) lastText = t;
      lastStop = m.stopReason || lastStop;
      if (m.errorMessage) lastError = m.errorMessage;
    } else if (m.role === 'toolResult') {
      events.push({ type: 'tool_result', callId: m.toolCallId, tool: m.toolName,
        status: m.isError ? 'error' : 'completed', result: text(m.content) });
    } else if (m.role === 'user') {
      events.push({ type: 'user', text: text(m.content) });
    }
  });
  const reason = { kind: KIND[lastStop] || (lastStop ? lastStop : 'no_reply') };
  if (lastError) reason.error = lastError;
  return { events: [{ type: 'session', sessionId, cwd }, ...events, { type: 'final', sessionId, reason, text: lastText }], sessionId, final: lastText };
}

export function hashTree(root) {
  const out = {};
  const skip = new Set(['node_modules', '.git', '__pycache__']);
  (function walk(d) {
    let entries;
    try { entries = readdirSync(d, { withFileTypes: true }); } catch { return; }
    for (const e of entries) {
      if (skip.has(e.name)) continue;
      const p = join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.isFile()) { try { out[relative(root, p)] = createHash('sha256').update(readFileSync(p)).digest('hex'); } catch { /* unreadable: skip */ } }
    }
  })(root);
  return out;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const [n, dir, start] = process.argv.slice(2);
  const logs = process.env.RAE_LOGS || '/logs/agent';
  const file = sessionFile(dir);
  const lines = file ? readFileSync(file, 'utf8').split('\n').filter((l) => l.trim()) : [];
  const { events, sessionId, final } = convert(lines, Number(start) || 0);
  const cwd = events[0].cwd;
  writeFileSync(join(logs, `events-${n}.jsonl`), events.map((e) => JSON.stringify(e)).join('\n') + '\n');
  writeFileSync(join(logs, `final-${n}.txt`), final);
  writeFileSync(join(logs, `session-${n}.txt`), sessionId);
  writeFileSync(join(logs, `ws-${n}.json`), JSON.stringify(hashTree(process.env.RAE_WORKSPACE || cwd || '/app')));
  console.log(`rae-lines ${lines.length}`);
}
