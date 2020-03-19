import os
import json
from pathlib import Path

ROOT = Path(os.path.dirname(__file__)) / '..'

output = {}
for chart in sorted((ROOT / 'output' / 'charts').iterdir(), reverse=True):
    date, code = chart.name.split('.')[0].split('_', 1)[:2]
    output[code] = output.get(code, {})
    output[code][date] = str(chart.relative_to(ROOT / 'output'))

with open(ROOT / 'output' / 'charts.json', 'w') as fh:
    output_sorted = {key: output[key] for key in sorted(output.keys())}
    json.dump(output_sorted, fh)