import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_slides import check
from package_slides import package

FRONT = '---\nmarp: true\ntheme: aizome\n---\n'


class StaticChecks(unittest.TestCase):
    def run_deck(self, source, files=None):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, contents in (files or {}).items():
                (root / name).write_text(contents)
            deck = root / 'deck.md'
            deck.write_text(FRONT + source)
            return check(deck)

    def codes(self, report):
        return {f['code'] for f in report['findings']}

    def test_contract_references_are_consistent(self):
        import re
        catalog = json.loads((ROOT / 'ai/layouts.json').read_text())
        available = set(catalog['layouts']) | set(catalog['modifiers'])
        self.assertFalse(available & set(catalog['deprecated']))
        css = (ROOT / 'aizome.css').read_text()
        for name in available:
            # media-left explicitly selects media's default order; no extra CSS needed.
            self.assertTrue(name == 'media-left' or re.search(r'\.' + re.escape(name) + r'\b', css), name)
        for spec in catalog['modifiers'].values():
            for reference in spec.get('requiresAny', []) + spec.get('conflicts', []):
                self.assertIn(reference, available)
        for spec in catalog['layouts'].values():
            for variant in spec.get('limitVariants', []):
                self.assertLessEqual(variant['min'], variant['max'])
                self.assertTrue(set(variant['when']) <= available)

    def test_catalog_and_fixed_examples(self):
        for source in ['template.md', 'examples/repairs-after.md']:
            report = check(ROOT / source)
            self.assertEqual((report['errors'], report['warnings']), (0, 0), report)

    def test_broken_example_is_detected(self):
        codes = self.codes(check(ROOT / 'examples/repairs-before.md'))
        self.assertTrue({'item-count', 'conflicting-modifiers', 'missing-source', 'page-link'} <= codes)

    def test_fenced_examples_do_not_create_slides_or_errors(self):
        report = self.run_deck('# Title\n```markdown\n---\n<!-- _class: kpi -->\n![x](missing.png)\n```\n')
        self.assertEqual((report['slides'], report['errors']), (1, 0))

    def test_unclosed_fence_is_not_silently_ignored(self):
        self.assertIn('syntax', self.codes(self.run_deck('# Title\n```\nhello')))

    def test_deprecated_and_unknown_are_distinct(self):
        report = self.run_deck('<!-- _class: kpi my-custom -->\n# Title')
        self.assertEqual(report['errors'], 1)
        self.assertEqual(report['warnings'], 1)

    def test_modifiers_and_structure(self):
        report = self.run_deck('<!-- _class: cards horizontal with-source with-notes -->\n# Title\nText')
        self.assertTrue({'modifier-without-layout', 'conflicting-modifiers', 'missing-list', 'notes-position', 'missing-source'} <= self.codes(report))

    def test_capacity_and_nested_items(self):
        report = self.run_deck('<!-- _class: cards -->\n# Title\n- A\n  - nested\n- B\n')
        self.assertEqual(report['errors'] + report['warnings'], 0)
        report = self.run_deck('<!-- _class: timeline split -->\n# Title\n' + '\n'.join(f'{i}. Event' for i in range(1, 11)))
        self.assertNotIn('item-count', self.codes(report))

    def test_named_links_and_duplicates(self):
        source = '# Title\n###### 表1：プラン比較\n[表1](#表1プラン比較)\n---\n# More\n###### 表1：プラン比較'
        codes = self.codes(self.run_deck(source))
        self.assertIn('duplicate-caption', codes)
        self.assertNotIn('heading-link', codes)

    def test_missing_images_and_page_range(self):
        report = self.run_deck('# Title\n![x](missing.png)\n[2枚目](#1)\n[99枚目](#99)')
        self.assertTrue({'missing-image', 'page-label', 'page-link'} <= self.codes(report))

    def test_reference_style_image(self):
        report = self.run_deck('# Title\n![x][photo]\n\n[photo]: missing.png')
        self.assertIn('missing-image', self.codes(report))


class Packaging(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.html = self.root / 'deck.html'
        self.output = self.root / 'deck.zip'

    def test_relocation_css_assets_remote_and_navigation(self):
        (self.root / 'style').mkdir()
        (self.root / 'style/theme.css').write_text('@import "more.css"; p {background:url("../photo.svg")}')
        (self.root / 'style/more.css').write_text('h1 { color: blue }')
        (self.root / 'photo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (self.root / 'private.md').write_text('not part of the presentation')
        self.html.write_text('<html><link rel="stylesheet" href="style/theme.css"><img src="photo.svg"><img src="https://example.com/a.svg"><a href="private.md">private</a><script>const x = "<tag>";</script></html>')
        report = package(self.html, self.output)
        self.assertEqual(report['resourceCount'], 3)
        self.assertEqual(report['externalResources'], ['https://example.com/a.svg'])
        self.assertEqual(report['localNavigationNotBundled'], ['private.md'])
        with zipfile.ZipFile(self.output) as z:
            self.assertNotIn('private.md', z.namelist())
            html = z.read('index.html').decode()
            self.assertIn('const x = "<tag>";', html)
            self.assertNotIn('src="photo.svg"', html)
            css = next(z.read(n).decode() for n in z.namelist() if n.endswith('-theme.css'))
            self.assertNotIn('../photo', css)
            self.assertNotIn('assets/', css)  # relative from packaged CSS, not HTML
            manifest = json.loads(z.read('manifest.json'))
            self.assertEqual(manifest['resourceCount'], 3)

    def test_missing_asset_leaves_no_zip(self):
        self.html.write_text('<img src="missing.svg">')
        with self.assertRaisesRegex(ValueError, 'Missing'):
            package(self.html, self.output)
        self.assertFalse(self.output.exists())

    def test_path_escape(self):
        self.html.write_text('<img src="../private.txt">')
        with self.assertRaisesRegex(ValueError, 'outside'):
            package(self.html, self.output)

    def test_cycle_and_svg_dependency_fail_clearly(self):
        (self.root / 'a.css').write_text('@import "a.css";')
        self.html.write_text('<link rel="stylesheet" href="a.css">')
        with self.assertRaisesRegex(ValueError, 'Circular'):
            package(self.html, self.output)
        (self.root / 'image.svg').write_text('<svg><image href="other.png"/></svg>')
        self.html.write_text('<img src="image.svg">')
        with self.assertRaisesRegex(ValueError, 'SVG must embed'):
            package(self.html, self.output)

    def test_font_license_and_no_overwrite(self):
        fonts = self.root / 'assets/fonts'
        fonts.mkdir(parents=True)
        (fonts / 'font.woff').write_bytes(b'font')
        (fonts / 'OFL.txt').write_text('license')
        self.html.write_text('<style>@font-face{src:url("assets/fonts/font.woff")}</style>')
        package(self.html, self.output)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.read('licenses/MPLUSRounded1c-OFL.txt'), b'license')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            package(self.html, self.output)

    def test_data_uri_and_base(self):
        self.html.write_text('<img src="data:image/png;base64,AA==">')
        self.assertEqual(package(self.html, self.output)['resourceCount'], 0)
        other = self.root / 'other.zip'
        self.html.write_text('<base href="https://example.com">')
        with self.assertRaisesRegex(ValueError, 'base'):
            package(self.html, other)

    def test_reproducible_archive(self):
        self.html.write_text('<h1>Hello</h1>')
        package(self.html, self.output)
        second = self.root / 'second.zip'
        package(self.html, second)
        self.assertEqual(self.output.read_bytes(), second.read_bytes())


if __name__ == '__main__':
    unittest.main()
