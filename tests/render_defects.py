"""Seed real rendering failures into built HTML, or verify their detection."""
import json
from pathlib import Path
import re
import sys

if sys.argv[1] == '--verify':
    report = json.loads(Path(sys.argv[2]).read_text())
    codes = {f['code'] for f in report['findings']}
    expected = {'overflow', 'title-clearance', 'missing-image', 'missing-background', 'broken-fragment'}
    assert expected <= codes, f'Missing detections: {expected - codes}'
    print('Detected all seeded rendering failures.')
else:
    html = Path(sys.argv[1]).read_text()
    html = html.replace('</head>', '''<style>
section.cards > ul { transform:translateY(800px); }
section.lead > h2 { position:absolute;top:36px; }
</style></head>''')
    html = re.sub(r'(<section\b[^>]*\bid="1"[^>]*>)', r'\1<img src="assets/missing-fixture.png" alt="Missing fixture" width="16" height="16"><a href="#99999">Missing page</a>', html, count=1)
    html = html.replace('assets/placeholder-rail.svg', 'assets/missing-background.svg')
    Path(sys.argv[2]).write_text(html)
