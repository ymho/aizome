#!/usr/bin/env python3
"""Dependency-free checks for Aizome's documented Markdown subset."""
import argparse
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[1]


def visible_lines(text):
    """Blank fenced examples while preserving line positions (including list fences)."""
    out, fence = [], None
    for line in text.splitlines():
        match = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                fence = None
            out.append('')
        elif match:
            fence = match[1]
            out.append('')
        else:
            out.append(line)
    return '\n'.join(out), fence


def parse_deck(text):
    lines = text.splitlines()
    front = ''
    if lines and lines[0].strip() == '---':
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
        if end is None:
            return '', [], 'Front Matterが閉じていません。'
        front, text = '\n'.join(lines[1:end]), '\n'.join(lines[end + 1:])
    clean, fence = visible_lines(text)
    return front, re.split(r'^---\s*$', clean, flags=re.M), 'コードフェンスが閉じていません。' if fence else None


def slug(text):
    text = re.sub(r'!?\[([^]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'<[^>]*>', '', text).strip().lower().replace(' ', '-')
    return ''.join(c for c in text if c in '-_' or not unicodedata.category(c).startswith(('P', 'S', 'C')))


def check(path, catalog=None):
    catalog = catalog or json.loads((REPO / 'ai/layouts.json').read_text())
    path = Path(path)
    text = path.read_text(encoding='utf-8-sig')
    front, slides, parse_error = parse_deck(text)
    findings = []
    def issue(level, code, message, slide=None):
        findings.append(dict(severity=level, code=code, slide=slide, message=message))
    if parse_error:
        issue('error', 'syntax', parse_error)
    if not re.search(r'^marp:\s*true\s*$', front, re.M):
        issue('error', 'front-matter', 'marp: true が必要です。')
    if not re.search(r'^theme:\s*[\'"]?aizome[\'"]?\s*$', front, re.M):
        issue('error', 'theme', 'theme: aizome を指定してください。')
    if re.search(r'^class:', front, re.M):
        issue('warning', 'global-class', 'Front Matterのclass継承は静的判定の対象外です。_classを推奨します。')
    headings, duplicates, links = {}, {}, []
    for number, slide in enumerate(slides, 1):
        directives = re.findall(r'<!--\s*_class:\s*(.*?)\s*-->', slide, re.S)
        classes = directives[-1].strip('"\' ').split() if directives else []
        if len(directives) > 1:
            issue('warning', 'multiple-class-directives', '_classは1枚に1つへまとめてください。', number)
        if re.search(r'<!--\s*class:', slide):
            issue('warning', 'global-class', 'class継承は静的判定の対象外です。_classを推奨します。', number)
        bases = [c for c in classes if c in catalog['layouts']]
        if len(bases) > 1:
            issue('error', 'conflicting-layouts', '基本レイアウトは1つ: ' + ', '.join(bases), number)
        groups = {}
        for c in classes:
            if c in catalog['deprecated']:
                issue('error', 'deprecated-class', f'{c} → {catalog["deprecated"][c]}', number)
            elif c not in catalog['layouts'] and c not in catalog['modifiers']:
                issue('warning', 'unknown-class', f'{c}: 契約にありません。独自CSSなら表示を確認してください。', number)
            spec = catalog['modifiers'].get(c, {})
            group = spec.get('exclusiveGroup')
            if group:
                if group in groups:
                    issue('error', 'conflicting-modifiers', f'{groups[group]} と {c} は同時指定できません。', number)
                groups[group] = c
            if spec.get('requiresAny') and not set(spec['requiresAny']).intersection(classes):
                issue('error', 'modifier-without-layout', f'{c} は {spec["requiresAny"]} と使います。', number)
            conflicts = set(spec.get('conflicts', [])).intersection(classes)
            if conflicts:
                issue('error', 'incompatible-class', f'{c} と {sorted(conflicts)} の併用を避けてください。', number)
        content = re.sub(r'<!--.*?-->', '', slide, flags=re.S)
        # Inline code is literal, not HTML or a reference.
        content = re.sub(r'(`+).*?\1', '', content)
        if re.search(r'</?(?:div|span|br|table|img|iframe|script)\b', content, re.I):
            issue('error', 'raw-html', '本文のHTMLタグをMarkdownと共通クラスに置き換えてください。', number)
        h1s = re.findall(r'^# (.+)$', content, re.M)
        if len(h1s) > 1 or (not h1s and 'no-title' not in classes):
            issue('warning', 'title-count', 'h1は1枚につき1つ（no-titleは省略可能）を推奨します。', number)
        for hashes, title in re.findall(r'^(#{1,6})\s+(.+)$', content, re.M):
            key = slug(title)
            count = duplicates.get(key, 0)
            if len(hashes) == 6 and count:
                issue('error', 'duplicate-caption', f'図表名が重複しています: {title}', number)
            duplicates[key] = count + 1
            headings[key + (f'-{count}' if count else '')] = number
        unordered = len(re.findall(r'^[-+*]\s+', content, re.M))
        ordered = len(re.findall(r'^\d+[.)]\s+', content, re.M))
        for base in bases:
            spec = catalog['layouts'][base]
            kind = spec.get('listType')
            count = ordered if kind == 'ordered' else unordered if kind == 'unordered' else ordered + unordered
            if kind and not count:
                issue('error', 'missing-list', f'{base}: トップレベルの{kind}リストが必要です。', number)
            minimum, maximum = spec.get('recommendedMinItems', 1), spec.get('recommendedMaxItems')
            for variant in spec.get('limitVariants', []):
                if set(variant['when']).issubset(classes):
                    minimum, maximum = variant['min'], variant['max']
            if kind and (count < minimum or (maximum and count > maximum)):
                issue('warning', 'item-count', f'{base}: {count}項目。目安は{minimum}〜{maximum or "制限なし"}。', number)
        if 'cards' in classes:
            if {'wide-left', 'wide-right', 'equal', 'before-after'}.intersection(classes) and unordered != 2:
                issue('error', 'two-card-option', '幅変更・before-afterは2カード用です。', number)
            if 'focus-center' in classes and unordered != 3:
                issue('error', 'three-card-option', 'focus-centerは3カード用です。', number)
        if 'with-notes' in classes and not re.search(r'^>.*\S', content.rstrip().split('\n')[-1]):
            issue('error', 'notes-position', 'with-notesの最後の要素は引用ブロックです。', number)
        if 'with-source' in classes and not re.search(r'<!--\s*_footer:', slide):
            issue('error', 'missing-source', 'with-sourceには_footerを指定してください。', number)
        if 'section-title' in classes and 'no-title' not in classes and not re.search(r'<!--\s*_header:', slide):
            issue('warning', 'missing-section-header', 'section-titleには_headerを指定してください。', number)
        # Include footer/header resources, but not code examples.
        refs = re.sub(r'(`+).*?\1', '', slide)
        definitions = dict(re.findall(r'^\s*\[([^]]+)\]:\s*<?([^\s>]+)>?', refs, re.M))
        refs = re.sub(r'(!?\[[^]\n]*\])\[([^]]+)\]', lambda m: m[1] + '(' + definitions.get(m[2], '') + ')', refs)
        for image, label, url in re.findall(r'(!?)\[([^]\n]*)\]\(\s*<?([^\s)>]+)>?(?:\s+["\'][^\n]*?["\'])?\s*\)', refs):
            target = urlsplit(url)
            if target.scheme or target.netloc:
                continue
            if not target.path and target.fragment:
                if not image:
                    links.append((number, label, unquote(target.fragment)))
            elif target.path and not (path.parent / unquote(target.path)).exists():
                issue('error', 'missing-image' if image else 'missing-file', f'参照先がありません: {target.path}', number)
    for number, label, target in links:
        if target.isdigit():
            if not 1 <= int(target) <= len(slides):
                issue('error', 'page-link', f'#{target} は全{len(slides)}枚の範囲外です。', number)
            match = re.match(r'^(\d+)(?:[〜～–-](\d+))?枚目$', label)
            if match and (int(match[1]) != int(target) or (match[2] and not int(target) <= int(match[2]) <= len(slides))):
                issue('error', 'page-label', f'ページ表示 {label} とリンク #{target} を確認してください。', number)
        elif target not in headings:
            issue('warning', 'heading-link', f'#{target} を静的に解決できません。HTMLのidを確認してください。', number)
    return {'schemaVersion': 1, 'file': str(path), 'slides': len(slides), 'scope': 'static-markdown-subset',
            'errors': sum(f['severity'] == 'error' for f in findings),
            'warnings': sum(f['severity'] == 'warning' for f in findings), 'findings': findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', type=Path)
    parser.add_argument('--json', action='store_true', help='Agent向けJSONを出力')
    parser.add_argument('--strict', action='store_true', help='警告も終了コード1にする')
    args = parser.parse_args()
    try:
        result = check(args.markdown)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f'{result["slides"]} slides: {result["errors"]} errors, {result["warnings"]} warnings')
        for f in result['findings']:
            print(f'{f["severity"]} slide {f["slide"] or "-"} [{f["code"]}]: {f["message"]}')
    return int(bool(result['errors'] or (args.strict and result['warnings'])))


if __name__ == '__main__':
    sys.exit(main())
