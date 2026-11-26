# Frame-rate report for one play session, following docs/klbf/MEASUREMENT.md.
# Usage: python fps-session.py <log file>   (the runtime's stderr log)
# Reads the per-second "N fps, ... M draws/frame" lines; keeps samples with the world on screen (>= 1000 draws).
import re, sys
ansi = re.compile(r'\x1b\[[0-9;]*m')
v = []
for line in open(sys.argv[1], encoding='utf8', errors='ignore'):
    m = re.search(r' ([0-9.]+) fps,.*?(\d+) draws/frame', ansi.sub('', line))
    if m and int(m.group(2)) >= 1000:
        v.append(float(m.group(1)))
if not v:
    sys.exit('no world samples found')
v.sort(); n = len(v)
low = lambda p: sum(v[:max(1, n * p // 100)]) / max(1, n * p // 100)
print(f'Average performance index: average {sum(v)/n:.1f} fps, median {v[n//2]:.1f}, 5 % low {low(5):.1f}, 1 % low {low(1):.1f} ({n} samples)')
print('Stability index:')
for lo, hi, name in [(18, 1e9, '18 and more'), (15, 18, '15-18'), (12, 15, '12-15'), (9, 12, '9-12'), (5, 9, '5-9'), (0, 5, 'under 5')]:
    print(f'  {name:12} {100 * sum(lo <= x < hi for x in v) / n:3.0f} %')
