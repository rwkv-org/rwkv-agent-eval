"""Pass when the answer names a UTC time within 10 minutes of now."""
import datetime as dt
import re
import sys

text = open(sys.argv[1]).read() if len(sys.argv) > 1 else ''
now = dt.datetime.now(dt.timezone.utc)
for h, m in re.findall(r'\b([01]?\d|2[0-3])[:：]([0-5]\d)\b', text):
    t = now.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
    gap = min(abs((t - now).total_seconds()), 86400 - abs((t - now).total_seconds()))
    if gap <= 600:
        print(f'PASS {h}:{m} vs now {now:%H:%M}')
        sys.exit(0)
print(f'FAIL no time within 10 min of {now:%H:%M} UTC in: {text[:200]!r}')
sys.exit(1)
