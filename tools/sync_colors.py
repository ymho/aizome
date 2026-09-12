#!/usr/bin/env python3
"""Synchronize committed CSS color tokens from ai/colors.json (maintainer tool)."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
START = '/* BEGIN GENERATED COLORS: tools/sync_colors.py */'
END = '/* END GENERATED COLORS */'
PALETTE_START = '/* BEGIN GENERATED PALETTES: tools/sync_colors.py */'
PALETTE_END = '/* END GENERATED PALETTES */'


def kebab(name):
    return re.sub(r'[A-Z]', lambda m: '-' + m[0].lower(), name)


def generated(data):
    tokens = [START, 'section {']
    for name, value in data['neutral'].items():
        tokens.append(f'  --iro-{name}: {value};')
    for name, palette in data['palettes'].items():
        for role, value in palette.items():
            if role != 'name':
                tokens.append(f'  --iro-{name}-{kebab(role)}: {value};')
    tokens.extend(['}', END])
    lines = [PALETTE_START]
    markers = []
    for index, (name, palette) in enumerate(data['palettes'].items(), 1):
        selectors = ['section'] if name == data['defaultPalette'] else []
        selectors += [f'section.palette-{name}', f'section.palette-catalog > ul > li:nth-child({index})']
        lines.append(',\n'.join(selectors) + ' {')
        roles = {'accent':'accent', 'accent-soft':'soft', 'bg-tint':'tint', 'heading':'heading', 'deep':'deep',
                 'palette-dark-panel':'dark-panel', 'palette-dark-tint':'dark-panel-tint', 'palette-dark-line':'dark-line',
                 'palette-dark-accent':'soft', 'marker-light':'soft', 'marker-dark':'dark-marker'}
        for prop, role in roles.items():
            lines.append(f'  --{prop}: var(--iro-{name}-{role});')
        lines.append('}')
        markers.append(f'section.marker-{name} {{ --marker-light: var(--iro-{name}-soft); --marker-dark: var(--iro-{name}-dark-marker); }}')
    lines.extend(markers)
    lines.append(PALETTE_END)
    return '\n'.join(tokens), '\n'.join(lines)


def sync(check_only=False):
    data = json.loads((ROOT / 'ai/colors.json').read_text())
    css_file = ROOT / 'aizome.css'
    css = css_file.read_text()
    result = css
    for start, end, block in zip([START, PALETTE_START], [END, PALETTE_END], generated(data)):
        pattern = re.escape(start) + r'.*?' + re.escape(end)
        if len(re.findall(pattern, result, re.S)) != 1:
            raise ValueError('Expected one generated color block: ' + start)
        result = re.sub(pattern, lambda _: block, result, flags=re.S)
    if check_only:
        return result == css
    css_file.write_text(result)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if not sync(args.check):
        print('Color definitions differ. Run: python3 tools/sync_colors.py', file=sys.stderr)
        sys.exit(1)
