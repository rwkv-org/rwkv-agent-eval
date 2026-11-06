"""Re-judge finished trials for judge fixes made after they ran.

Tasks carry their own copy of bank/judge.py (tests/judge.py), so trials judged
before a fix keep the old verdict. `rejudged_reward` applies each later fix to
a trial's verifier/details.json, so runs judged before and after score alike:

  2026-11-07  DSH viewing-tool names (read/grep/glob/bash) stand in for each
              other in required_tools, as old names always did. A failed trial
              whose only failures are "required tool <viewing> not called" in
              turns that did call another viewing tool now passes.
"""
import json
import re
from pathlib import Path

VIEW = {'read', 'grep', 'glob', 'bash'}


def rejudged_reward(trial_dir, reward):
    if reward >= 1:
        return reward
    try:
        det = json.loads((Path(trial_dir) / 'verifier' / 'details.json').read_text())
    except (OSError, json.JSONDecodeError):
        return reward
    if det.get('case'):
        return reward
    hit = False
    for t in det.get('turns') or []:
        for m in t.get('failures') or []:
            g = re.match(r'required tool (\w+) not called$', m)
            if not (g and g.group(1) in VIEW and set(t.get('tools') or []) & VIEW):
                return reward
            hit = True
    return 1.0 if hit else reward
