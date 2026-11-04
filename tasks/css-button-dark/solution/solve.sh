#!/usr/bin/env bash
python3 - <<'PY'
p = 'css/site.css'
s = open(p).read()
s = s.replace('background-color: #2f6fed;', 'background-color: #000000;').replace('color: #f5f5f5;', 'color: #ffffff;')
open(p, 'w').write(s)
PY
