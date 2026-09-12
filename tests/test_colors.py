import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_colors import sync, START, END


def luminance(hex_value):
    channels = [int(hex_value[i:i+2], 16) / 255 for i in [1, 3, 5]]
    channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(a*b for a, b in zip(channels, [.2126, .7152, .0722]))


def contrast(a, b):
    light, dark = sorted([luminance(a), luminance(b)], reverse=True)
    return (light + .05) / (dark + .05)


class SharedColors(unittest.TestCase):
    def test_css_is_synced_and_components_have_no_color_literals(self):
        self.assertTrue(sync(True))
        css = (ROOT / 'aizome.css').read_text()
        without_tokens = re.sub(re.escape(START) + '.*?' + re.escape(END), '', css, flags=re.S)
        self.assertFalse(re.search(r'#[a-fA-F0-9]{3,8}\b|rgba?\(', without_tokens))

    def test_names_and_marker_contrast(self):
        data = json.loads((ROOT / 'ai/colors.json').read_text())
        for name, palette in data['palettes'].items():
            self.assertRegex(name, r'^[a-z]+$')
            self.assertFalse(re.search('[ァ-ヶ]', palette['name']))
            self.assertGreaterEqual(contrast(data['neutral']['sumi'], palette['soft']), 4.5)
            self.assertGreaterEqual(contrast(data['neutral']['yoiro'], palette['darkMarker']), 4.5)

    def test_contract_uses_the_same_palette_names(self):
        colors = json.loads((ROOT / 'ai/colors.json').read_text())['palettes']
        contract = json.loads((ROOT / 'ai/layouts.json').read_text())
        for prefix in ['palette-', 'marker-']:
            names = {name.removeprefix(prefix) for name in contract['modifiers'] if name.startswith(prefix)}
            self.assertEqual(names, set(colors))

    def test_dark_foregrounds_are_readable_on_code_backgrounds(self):
        data = json.loads((ROOT / 'ai/colors.json').read_text())
        palettes = data['palettes'].values()
        backgrounds = [data['neutral']['kuro']] + [p['darkPanel'] for p in palettes]
        for palette in palettes:
            self.assertNotEqual(palette['darkAccent'], palette['soft'])
            for background in backgrounds:
                self.assertGreaterEqual(contrast(palette['darkAccent'], background), 4.5)
