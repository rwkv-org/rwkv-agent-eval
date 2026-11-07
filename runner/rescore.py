"""Re-judge finished trials for judge fixes made after they ran.

Tasks carry their own copy of bank/judge.py (tests/judge.py), so trials judged
before a fix keep the old verdict. `rejudged_reward` applies each later fix to
a trial's verifier/details.json, so runs judged before and after score alike:

  2026-11-07  DSH viewing-tool names (read/grep/glob/bash) stand in for each
              other in required_tools, as old names always did. A failed trial
              whose only failures are "required tool <viewing> not called" in
              turns that did call another viewing tool now passes.
  2026-11-07  own-wc-073/078/083/087/090: turn 2 asks for a new result file
              but its expect carried unchanged_files, which makes it a
              read-only turn (no write/edit). Dropped from the cases; the
              "read-only turn used ..." failure of that turn no longer counts.
"""
import json
import re
from pathlib import Path

VIEW = {'read', 'grep', 'glob', 'bash'}
WRITE_TURN_FIXED = {f'own-wc-0{n}': 2 for n in (73, 78, 83, 87, 90)}


def forgiven(task, turn, tools, msg):
    g = re.match(r'required tool (\w+) not called$', msg)
    if g and g.group(1) in VIEW and set(tools) & VIEW:
        return True
    return WRITE_TURN_FIXED.get(task) == turn and msg.startswith('read-only turn used ')


def rejudged_reward(trial_dir, reward):
    if reward >= 1:
        return reward
    try:
        det = json.loads((Path(trial_dir) / 'verifier' / 'details.json').read_text())
    except (OSError, json.JSONDecodeError):
        return reward
    if det.get('case'):
        return reward
    task = Path(trial_dir).name.split('__')[0]
    hit = False
    for t in det.get('turns') or []:
        for m in t.get('failures') or []:
            if not forgiven(task, t.get('turn'), t.get('tools') or [], m):
                return reward
            hit = True
    return 1.0 if hit else reward
