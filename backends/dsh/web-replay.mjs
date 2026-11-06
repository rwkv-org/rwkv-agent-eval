// DSH overlay plugin for evals: web_search / web_fetch answered from an
// archive of real, previously captured responses (provider id `replay`), so
// web tasks score the same on every run and never touch the network.
//
// Installed by backends/dsh/harbor_agent.py inside the DSH package directory
// (so `@deepseek-ai/dsh-web` resolves) and enabled through the headless
// profile. The archive path comes in $RAE_WEB_ARCHIVE. The plugin only reads
// it: DSH loads plugins in a launcher process before forking the runtime, so
// deleting the variable or file at load would leave the runtime with nothing.
// The backend deletes the file after each turn. The archive holds only the real
// pages the task wants fetched, not answers; a model that reads it with bash
// instead of web_fetch still fails the task's required_tools check.
//
// Archive (JSON):
//   search_mode  "replay" (default): unmatched queries return no results, like
//                the training fixture; "unavailable": every search fails with
//                the message real-web training cases saw.
//   search       [{match: [keyword...], results: [{url, title, snippet, publishedAt}]}]
//                a query uses the entry whose keywords it contains most (>= 1).
//   pages        [{url, finalUrl, status, contentType, body}]  (pipeline snapshots.jsonl rows)
// With no archive at all, searches return nothing and fetches fail with 404:
// what non-web training cases saw.

import { readFileSync } from 'node:fs'
import { WebError } from '@deepseek-ai/dsh-web'

export const name = 'rae-web-replay'
export const inject = ['web']

const MAX_CHARS = 200_000

function load() {
  const path = process.env.RAE_WEB_ARCHIVE
  if (!path) return {}
  try {
    return JSON.parse(readFileSync(path, 'utf8'))
  } catch {
    return {}
  }
}

const archive = load()
const searches = archive.search ?? []
const pages = new Map()
for (const page of archive.pages ?? []) {
  const key = normalize(page.url)
  if (!pages.has(key)) pages.set(key, page)  // first capture wins: what the source showed first
}

function normalize(url) {
  return String(url).split('#')[0].replace(/\/+$/, '').replace(/^http:\/\//, 'https://')
}

const fetched = new Map()

export function apply(ctx) {
  ctx.web.registerSearchProvider({
    id: 'replay',
    title: 'Archived search',
    available: () => true,
    search: async (request) => {
      if (archive.search_mode === 'unavailable') {
        throw new WebError('live search is not configured; open the URL from the task', 'WEB_PROVIDER_ERROR')
      }
      const query = String(request.query ?? '').toLowerCase()
      let best, bestHits = 0
      for (const entry of searches) {
        const hits = (entry.match ?? []).filter(k => query.includes(String(k).toLowerCase())).length
        if (hits > bestHits) { best = entry; bestHits = hits }
      }
      const max = request.maxResults ?? 10
      return {
        sources: (best?.results ?? []).slice(0, max).map(r => ({
          url: r.url,
          ...r.title ? { title: r.title } : {},
          ...r.snippet ? { snippet: r.snippet } : {},
          ...r.publishedAt ? { publishedAt: r.publishedAt } : {},
        })),
        truncated: false,
      }
    },
  })
  ctx.web.registerFetchProvider({
    id: 'replay',
    title: 'Archived pages',
    available: () => true,
    fetch: async (request) => {
      const base = normalize(request.url)
      const prev = fetched.get(base)
      if (prev) {
        // Same note the real-web training plugin gave on a repeat fetch.
        const note = `<p>Note: this page was already fetched in this session at ${base}. ` +
          `A #fragment is not sent to the server, so the response is identical; the earlier result was ` +
          `truncated and its full text is in the listed spill file (use read with offset/limit, or grep).</p>`
        const body = (note + prev.body).slice(0, MAX_CHARS)
        return { url: prev.finalUrl, statusCode: prev.status, body: { kind: prev.kind, content: body }, truncated: true }
      }
      const page = pages.get(base)
      if (!page) throw new WebError('HTTP 404', 'WEB_PROVIDER_ERROR')
      const status = page.status ?? 200
      if (status >= 400) throw new WebError(`HTTP ${status}`, 'WEB_PROVIDER_ERROR')
      const body = String(page.body ?? '').slice(0, MAX_CHARS)
      const kind = String(page.contentType ?? '').includes('html') ? 'html' : 'text'
      const finalUrl = page.finalUrl ?? page.url
      fetched.set(base, { finalUrl, status, kind, body })
      return { url: finalUrl, statusCode: status, body: { kind, content: body }, truncated: body.length >= MAX_CHARS }
    },
  })
}
