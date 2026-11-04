import re
import sys

css = open('css/site.css').read().lower()
rules = {m.group(1).strip(): m.group(2) for m in re.finditer(r'([^{}]+)\{([^}]*)\}', css)}

def props(selector):
    body = rules.get(selector, '')
    return {k.strip(): v.strip() for k, v in (p.split(':', 1) for p in body.split(';') if ':' in p)}

def color(v):
    v = v.replace(' ', '')
    return {'#000': '#000000', 'black': '#000000', '#fff': '#ffffff', 'white': '#ffffff'}.get(v, v)

btn, link = props('.btn-submit'), props('.btn-link')
checks = {
    'submit background black': color(btn.get('background-color', btn.get('background', ''))) == '#000000',
    'submit text white': color(btn.get('color', '')) == '#ffffff',
    'submit padding kept': btn.get('padding') == '0.5rem 1rem',
    'link untouched': link == {'background-color': '#eeeeee', 'color': '#333333'},
}
for name, ok in checks.items():
    print(('PASS ' if ok else 'FAIL ') + name)
sys.exit(0 if all(checks.values()) else 1)
