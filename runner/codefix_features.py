"""Per-trial behaviour features on code tasks for two runs (2026-11-07 r16 vs r64 drop analysis).

    PYTHONPATH=runner:. python3 runner/codefix_features.py <run A spec> <run B spec> <out.jsonl>

Specs as in attribution.py ('+'-joined job dirs). Blocks: code-fix, code-fix-oss
(HumanEvalFix), edit-code. Per trial: tool sequence, edits and failed edits
(tool result "ok":false), test runs (bash commands that look like a test run)
and the outcome of the last one ([exit code: N] in the DSH bash result), how
the run ended (trace `final ...` decisions), whether the final reply claims
success, and the judge's failure messages. Writes one JSON line per trial,
tagged model=r16 / r64 (A / B).
"""
import sys,json,re,glob,tomllib
from pathlib import Path
sys.path[:0]=['runner','.']
import attribution as at
BLOCKS={'code-fix','code-fix-oss','edit-code'}
TEST=re.compile(r'pytest|unittest|node --test|npm (run )?test|python3? -m (pytest|unittest)|go test|cargo test|\btest\.sh|run_tests|tests?/')
def outcome(resp):
  # DSH bash result: '{"ok":true,"tool":"bash","result":"...[exit code: N]"}'; no marker means exit 0
  if resp is None: return 'unknown'
  m=re.search(r'\[exit code: (\d+)\]',resp)
  if m: return 'fail' if m.group(1)!='0' else 'pass'
  if '"ok":false' in resp[:200]: return 'fail'
  if re.search(r'FAILED|[1-9]\d* failed|# fail [1-9]|not ok \d',resp[-3000:]): return 'fail'
  return 'pass'
def resp_after(prompt):
  i=prompt.rfind('<tool_response>')
  if i<0: return None
  j=prompt.find('</tool_response>',i)
  return prompt[i:j if j>0 else None]
CLAIM=re.compile(r'(全部|所有|均).{0,6}通过|测试.{0,4}通过|已(经)?修复|passed|all tests pass|修复完成',re.I)
meta={}
for d in ('build/bank-v1','build/bank-v1-fill','build/new-v2'):
  for t in Path(d).iterdir():
    m=tomllib.loads((t/'task.toml').read_text()).get('metadata',{}); meta[t.name]=m.get('block','oss') if 'humanevalfix' not in t.name else 'code-fix-oss'
out=open(sys.argv[3],'w')
for name,spec in (('r16',sys.argv[1]),('r64',sys.argv[2])):
  runs=at.load(spec)
  for tid,ts in runs.items():
    if meta.get(tid) not in BLOCKS: continue
    for t in ts:
      d=Path(t['dir']); recs=[]
      for f in sorted(glob.glob(str(d/'agent/trace/*'))):
        recs+=[json.loads(l) for l in open(f)]
      gens=[r for r in recs if 'prompt' in r]; steps=[r for r in recs if r.get('stage')=='step']
      tools=[s['decision'].split(' ',1)[1] for s in steps if s.get('decision','').startswith('tool ')]
      finals=[s['decision'] for s in steps if s.get('decision','').startswith('final')]
      edits_failed=0;tests=[];last_edit=-1;i_tool=0
      for idx,s in enumerate(steps):
        dec=s.get('decision','')
        if not dec.startswith('tool '): continue
        name_=dec.split(' ',1)[1]; args=s.get('args') or {}
        # the tool's result is at the end of the next generation's prompt
        r=None
        later=[g for g in gens if g['at']>s['at']]
        if later: r=resp_after(later[0]['prompt'])
        if name_ in('edit','write'):
          last_edit=idx
          if r and '"ok":false' in r[:200]: edits_failed+=1
        if name_=='bash' and TEST.search(str(args.get('command',''))):
          tests.append((idx,outcome(r)))
      final_txt=(d/'agent/final.txt').read_text(errors='ignore') if (d/'agent/final.txt').exists() else ''
      last_test=tests[-1][1] if tests else 'none'
      tested_after_edit=any(i>last_edit for i,_ in tests) if last_edit>=0 else None
      outs=[len(g.get('output','')) for g in gens]
      try: det=json.loads((d/'verifier/details.json').read_text()); fails=[m for tr in det.get('turns') or [] for m in tr.get('failures') or []]
      except Exception: fails=[]
      gate=sum(1 for g in gens if g.get('outcome') not in ('run','final'))
      out.write(json.dumps(dict(model=name,task=tid,block=meta[tid],dir=str(d),reward=t['reward'],timeout=bool(t['exc']),
        steps=len(tools),tools=tools,edits=sum(1 for x in tools if x in('edit','write')),edits_failed=edits_failed,
        tests=len(tests),tested_after_edit=tested_after_edit,last_test=last_test,
        final_via=finals,claims=bool(CLAIM.search(final_txt)),gens=len(gens),gate_events=gate,
        outcomes=sorted({g.get('outcome') for g in gens}),mean_out=sum(outs)/max(1,len(outs)),fails=fails[:3]),ensure_ascii=False)+'\n')
