#!/usr/bin/env python3
"""Bundle an exported HTML deck and its local rendering assets, without dependencies."""
import argparse
import hashlib
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

CSS_URL = re.compile(r'url\(\s*([\'"]?)(.*?)\1\s*\)', re.I)
CSS_IMPORT = re.compile(r'(@import\s+)([\'"])([^\'"]+)\2', re.I)


class Bundler:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.files = {}
        self.visiting = set()
        self.resources = {}
        self.remote = set()
        self.navigation = set()

    def asset(self, url, base, from_css=False):
        url = unescape(url.strip())
        parsed = urlsplit(url)
        if not url or url.startswith('#') or parsed.scheme == 'data':
            return url
        if parsed.scheme in ('https', 'http') or parsed.netloc:
            self.remote.add(url)
            return url
        if parsed.scheme:
            raise ValueError(f'Unsupported local resource scheme: {parsed.scheme}')
        source = (base / unquote(parsed.path)).resolve()
        if not source.is_relative_to(self.root):
            raise ValueError('Resource is outside --root: ' + parsed.path)
        if not source.is_file():
            raise ValueError('Missing resource: ' + parsed.path)
        if source in self.visiting:
            raise ValueError('Circular CSS imports: ' + parsed.path)
        if source not in self.resources:
            raw = source.read_bytes()
            key = str(source.relative_to(self.root)).encode() + b'\0' + raw
            safe_name = re.sub(r'[^\w.\-]', '_', source.name)
            name = 'assets/' + hashlib.sha256(key).hexdigest()[:16] + '-' + safe_name
            self.resources[source] = name
            self.visiting.add(source)
            if source.suffix.lower() == '.css':
                data = self.css(raw.decode('utf-8-sig'), source.parent, True).encode()
            elif source.suffix.lower() == '.svg':
                # SVGs with external embedded dependencies need explicit flattening.
                # Do not silently claim an offline bundle if an SVG fetches other files.
                svg = raw.decode('utf-8-sig')
                refs = re.findall(r'(?:href|src)=[\'"]([^\'"]+)', svg)
                refs += [m[1] for m in CSS_URL.findall(svg)]
                if any(not r.startswith(('#', 'data:')) for r in refs):
                    raise ValueError('SVG must embed its dependencies before packaging: ' + parsed.path)
                data = raw
            else:
                data = raw
            self.visiting.remove(source)
            self.files[name] = data
        name = self.resources[source]
        # All rewritten CSS assets live in the same assets directory.
        if from_css:
            name = name.removeprefix('assets/')
        return name + ('#' + parsed.fragment if parsed.fragment else '')

    def css(self, text, base, from_css=False):
        text = CSS_URL.sub(lambda m: 'url("' + self.asset(m[2], base, from_css) + '")', text)
        return CSS_IMPORT.sub(lambda m: m[1] + '"' + self.asset(m[3], base, from_css) + '"', text)


class Rewriter(HTMLParser):
    def __init__(self, bundler, base):
        super().__init__(convert_charrefs=False)
        self.bundle, self.base, self.parts, self.in_style = bundler, base, [], False

    def tag(self, tag, attrs):
        if tag == 'base':
            raise ValueError('HTML with <base> is not supported; export without a base URL.')
        attrs_dict = dict(attrs)
        rendered = []
        for key, value in attrs:
            if value is None:
                rendered.append(key)
                continue
            if key == 'srcset':
                raise ValueError('srcset requires explicit asset preparation before packaging.')
            resource = key in ('src', 'poster') or (tag == 'object' and key == 'data')
            resource |= tag == 'link' and key == 'href' and bool(set(attrs_dict.get('rel', '').split()) & {'stylesheet', 'icon', 'preload', 'modulepreload'})
            if resource:
                value = self.bundle.asset(value, self.base)
            elif key == 'style':
                value = self.bundle.css(value, self.base)
            elif tag == 'a' and key == 'href':
                u = urlsplit(value)
                if u.path and not u.scheme and not u.netloc:
                    self.bundle.navigation.add(value)
            rendered.append(key + '="' + escape(value, quote=True) + '"')
        raw = '<' + tag + (' ' + ' '.join(rendered) if rendered else '')
        return raw

    def handle_starttag(self, tag, attrs):
        self.parts.append(self.tag(tag, attrs) + '>')
        if tag == 'style':
            self.in_style = True

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.tag(tag, attrs) + '/>')

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        self.parts.append(self.bundle.css(data, self.base) if self.in_style else data)

    def handle_entityref(self, name): self.parts.append('&' + name + ';')
    def handle_charref(self, name): self.parts.append('&#' + name + ';')
    def handle_comment(self, data): self.parts.append('<!--' + data + '-->')
    def handle_decl(self, decl): self.parts.append('<!' + decl + '>')
    def handle_pi(self, data): self.parts.append('<?' + data + '>')


def package(html, output, root=None):
    html, output = Path(html).resolve(), Path(output).resolve()
    root = Path(root).resolve() if root else html.parent
    if output.exists():
        raise ValueError('Output already exists; choose a new ZIP filename.')
    bundle = Bundler(root)
    rewriter = Rewriter(bundle, root)
    rewriter.feed(html.read_text(encoding='utf-8-sig'))
    rewriter.close()
    bundle.files['index.html'] = ''.join(rewriter.parts).encode()
    # Carry the bundled font license when any of those fonts are included.
    font_dir = root / 'assets/fonts'
    if any(p.is_relative_to(font_dir) for p in bundle.resources):
        license_path = font_dir / 'OFL.txt'
        if not license_path.is_file():
            raise ValueError('Bundled font license assets/fonts/OFL.txt is missing.')
        bundle.files['licenses/MPLUSRounded1c-OFL.txt'] = license_path.read_bytes()
    manifest = {'schemaVersion': 1, 'entrypoint': 'index.html',
                'resourceCount': len(bundle.resources),
                'externalResources': sorted(bundle.remote),
                'localNavigationNotBundled': sorted(bundle.navigation),
                'files': [{'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                          for name, data in sorted(bundle.files.items())]}
    bundle.files['manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    bundle.files['README.txt'] = (
        'Aizome スライド配布用パッケージ\n\n'
        'ZIPをすべて展開し、index.htmlをブラウザで開いてください。assetsも同じ場所に残してください。\n'
        '画像・フォントは同梱しています。編集用ソースはこのパッケージに含めていません。\n'
        f'外部リソース: {len(bundle.remote)}件。絵文字などの表示には接続が必要な場合があります。\n'
        'manifest.jsonに外部依存と同梱ファイルの一覧を記録しています。\n'
        f'同梱していないローカル文書リンク: {len(bundle.navigation)}件。リンク先は別途共有してください。\n'
        '外部CSS・JavaScript内部の追加通信は静的には検出できません。配布前に別フォルダで表示確認してください。\n'
    ).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Build atomically; do not leave a partial release asset on failure.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as temporary:
        temp_path = Path(temporary.name)
    try:
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(bundle.files.items()):
                info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        temp_path.replace(output)
    finally:
        temp_path.unlink(missing_ok=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--root', type=Path, help='HTML内の相対リソースURLの基準。標準はHTMLのあるフォルダ。')
    args = parser.parse_args()
    try:
        manifest = package(args.html, args.output, args.root)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps({'output': str(args.output), 'resources': manifest['resourceCount'],
                      'externalResources': len(manifest['externalResources']),
                      'localNavigationNotBundled': len(manifest['localNavigationNotBundled'])}, ensure_ascii=False))


if __name__ == '__main__':
    main()
