// Request trace for the Pi backend: the exact bytes rwkv-pi sends to the engine
// and the raw stream it gets back, one file pair per request.
//
//   node --import /opt/rae-pi/trace.mjs ...      (RAE_TRACE_DIR=/logs/agent/trace)
//
// rwkv-pi renders Pi's messages into an RWKV prompt itself and posts it with its
// own undici import (src/transport.ts), so patching globalThis.fetch would miss
// it. undici publishes every request on node:diagnostics_channel, which is
// process-wide whichever undici copy sends it; this module only listens.
//
// Per request N (zero-padded, in send order):
//   N.request.json    {method, origin, path, body}   body parsed when JSON
//   N.response.txt    raw response body (SSE for /batch/completions)
//   N.meta.json       {status, startedAt, endedAt, error?}
// The Authorization header is never written.
import diagnostics from 'node:diagnostics_channel';
import { mkdirSync, writeFileSync, appendFileSync } from 'node:fs';
import { join } from 'node:path';

const dir = process.env.RAE_TRACE_DIR;
// Only engine traffic: the prompt is in /batch/completions; /tokens/count shows
// what rwkv-pi measured against the context budget.
const PATHS = (process.env.RAE_TRACE_PATHS || '/batch/completions,/tokens/count,/chat/completions').split(',');

if (dir) {
  mkdirSync(dir, { recursive: true });
  let next = 0;
  const live = new WeakMap();
  const name = (n) => String(n).padStart(4, '0');
  const traced = (path) => PATHS.some((p) => p && String(path || '').split('?')[0].endsWith(p));

  diagnostics.channel('undici:request:create').subscribe(({ request }) => {
    if (!traced(request.path)) return;
    const id = name(++next);
    const state = { id, chunks: [], startedAt: new Date().toISOString() };
    live.set(request, state);
    // Body is usually a string here (JSON.stringify in rwkv-pi); buffers arrive via bodyChunkSent.
    if (typeof request.body === 'string') state.chunks.push(request.body);
  });
  diagnostics.channel('undici:request:bodyChunkSent').subscribe(({ request, chunk }) => {
    const state = live.get(request);
    if (state) state.chunks.push(Buffer.from(chunk).toString('utf8'));
  });
  diagnostics.channel('undici:request:bodySent').subscribe(({ request }) => {
    const state = live.get(request);
    if (!state || state.written) return;
    state.written = true;
    // create() saw a string body and bodyChunkSent repeated it: keep one copy.
    const text = state.chunks.length > 1 && state.chunks[0] === state.chunks.slice(1).join('') ? state.chunks[0] : state.chunks.join('');
    let body = text;
    try { body = JSON.parse(text); } catch { /* not JSON: keep raw */ }
    writeFileSync(join(dir, `${state.id}.request.json`), JSON.stringify({ method: request.method, origin: String(request.origin || ''), path: request.path, body }, null, 1));
    writeFileSync(join(dir, `${state.id}.response.txt`), '');
  });
  diagnostics.channel('undici:request:headers').subscribe(({ request, response }) => {
    const state = live.get(request);
    if (state) state.status = response.statusCode;
  });
  diagnostics.channel('undici:request:bodyChunkReceived').subscribe(({ request, chunk }) => {
    const state = live.get(request);
    if (state) appendFileSync(join(dir, `${state.id}.response.txt`), Buffer.from(chunk));
  });
  const finish = (request, error) => {
    const state = live.get(request);
    if (!state) return;
    live.delete(request);
    writeFileSync(join(dir, `${state.id}.meta.json`), JSON.stringify({
      status: state.status ?? null, startedAt: state.startedAt, endedAt: new Date().toISOString(),
      ...(error ? { error: String(error.message || error) } : {}),
    }));
  };
  diagnostics.channel('undici:request:trailers').subscribe(({ request }) => finish(request));
  diagnostics.channel('undici:request:error').subscribe(({ request, error }) => finish(request, error));
}
