# Marp用スライドテンプレート（transit-tech）

PDF出力を優先したMarpテンプレート集です。HTMLをMarkdown内に書かず、Marp標準記法とクラス指定だけで構成しています。

## 使い方

VS Codeでこのフォルダを開いてください。`sample.md` 単体ではなく、必ずフォルダまたは `.code-workspace` を開きます。

```yaml
---
marp: true
theme: transit-tech-pdf
paginate: true
size: 16:9
---
```

## VS Code設定

`.vscode/settings.json` でカスタムテーマを登録しています。

```json
{
  "markdown.marp.themes": [
    "./transit-tech-pdf.css"
  ],
  "markdown.marp.exportType": "pdf"
}
```

ワークスペースが制限モードの場合、カスタムCSSが無効化されることがあります。フォルダを信頼済みにしてください。

## PDF出力

Marp拡張のメニューから出力してください。

```text
Export slide deck...
→ PDF
```

`Markdown PDF` など別拡張からの出力では、このテーマは適用されません。

## レイアウト例

```markdown
<!-- _class: cover -->
# 表紙

---
<!-- _class: section -->
# 中間タイトル

---
<!-- _class: image-right -->
![bg right:45% cover](assets/placeholder-rail.svg)
# 半分画像 / 半分文章
```

## 方針

- Markdown内にHTMLを書かない
- 複雑な装飾よりPDF安定性を優先する
- 半分画像は `![bg right:45% cover]` / `![bg left:45% cover]` を使う
- カードや2カラムはMarkdownのリストをCSSで整える
- コードブロックは言語名を必ず付ける
