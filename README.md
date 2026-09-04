# aizome

Aizomeは、**落ち着いた藍色を基調に、技術資料とビジネス資料の両方で使えるMarpテーマ**です。

`template.md` はそのまま複製して使えるサンプル兼レイアウトカタログになっています。

## Design principles

- **One slide, one message**：1枚で伝える主張を絞る
- **Quiet but strong**：装飾を増やしすぎず、見出しと余白で強弱をつける
- **Markdown first**：複雑なHTMLを書かず、Markdownと`_class`でレイアウトを切り替える
- **Business × Technical**：比較、KPI、意思決定、コード、図、画像を同じトーンで扱う

## 必要なもの

- [Visual Studio Code](https://code.visualstudio.com/)
- VS Code拡張機能 [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)

VS Codeの拡張機能ビューを開き、`Marp for VS Code` を検索してインストールしてください。

## 開き方

このリポジトリをクローンまたはダウンロードし、VS Codeでフォルダ全体を開きます。`template.md` だけを単独で開くとカスタムテーマの設定が読み込まれないため、必ずフォルダ、または `marp-aizome.code-workspace` を開いてください。

ワークスペースの信頼を求められた場合は、内容を確認したうえで信頼済みにします。制限モードではカスタムCSSが読み込まれないことがあります。

## プレビュー

1. VS Codeで `template.md` を開きます。
2. `Ctrl+K`、続けて `V` を押します。macOSでは `⌘+K`、続けて `V` を押します。

コマンドパレットから開く場合は、`Markdown: Open Preview to the Side` を実行します。Marp for VS Codeがインストールされ、Markdown先頭に `marp: true` があればスライドとして表示されます。

## 最小構成

新しい資料では、`template.md` をコピーし、不要なサンプルスライドを削除するのが最短です。

```yaml
---
marp: true
theme: aizome
paginate: true
size: 16:9
---
```

## Layout catalog

各スライドの直前に`<!-- _class: ... -->`を置くとレイアウトを切り替えられます。

| class | 用途 | Markdownの基本形 |
|---|---|---|
| `cover` | 表紙 | `#` + `##` + 著者 |
| `agenda` | 目次 | 番号付きリスト |
| `section` | 章扉 | `#` + `##` |
| `statement` | 一番伝えたい一文 | 最初の段落を大きく表示 |
| `cards` | 3論点 | トップレベルの箇条書き3つ |
| `columns` | 2カラム | トップレベルの箇条書き2つ |
| `compare` | Before / After | トップレベルの箇条書き2つ |
| `decision` | 意思決定 | 引用記法で結論を強調 |
| `process` | 4ステップ | 番号付きリスト4つ |
| `roadmap` | ロードマップ | 番号付きリスト4つ |
| `kpi` | KPI・大きな数字 | 箇条書き4つ + `**値**` |
| `quote` | 引用・思想 | 引用記法 |
| `table-center` | 表中心 | Markdown table |
| `image-right` | 右半分に画像 | Marp background image |
| `image-left` | 左半分に画像 | Marp background image |
| `full-image` | 全面画像 | Marp background image |
| `profile` | 自己紹介 | avatar画像 + 箇条書き |
| `success` | 成立条件・確認済み | 引用記法 |
| `warning` | 注意事項 | 引用記法 |
| `danger` | 重大リスク | 引用記法 |
| `dense` | Appendix | 小さめの本文・表・コード |
| `closing` | 締め | `#` + 短い一文 |

`cards` / `columns` / `compare` / `process` / `kpi` は、HTMLの`<div>`を書かなくてもMarkdownのリスト構造だけでレイアウトできます。

## よく使う例

### 一文を強く見せる

```markdown
<!-- _class: statement -->

# 一番伝えたいこと

**主語を「自分」に変えると、仕事の見え方が変わる。**
```

### Before / After

```markdown
<!-- _class: compare -->

# Before / After

- **Before**
  誰かが決める

- **After**
  自分で選ぶ
```

### プロセス

```markdown
<!-- _class: process -->

# 進め方

1. **Observe**
   現状を見る
2. **Choose**
   選ぶ
3. **Build**
   作る
4. **Learn**
   学ぶ
```

## ローカル開発

リポジトリには、LilyPond、Mermaid、PlantUMLから生成したSVGも含まれています。そのため、cloneしてスライドを表示・編集するだけなら、LilyPondなどの生成ツールを追加でインストールする必要はありません。

```text
music/example.ly                 → assets/generated/score.svg
diagrams/solution-flow.mmd       → assets/generated/mermaid.svg
diagrams/solver-sequence.puml    → assets/generated/plantuml.svg
```

MarkdownやCSSだけを編集した場合、SVGの再生成は不要です。`.ly`、`.mmd`、`.puml` のソースを編集した場合は、次のいずれかの方法でSVGを更新します。

### GitHub Pagesへ反映する

変更を `main` ブランチへpushすると、GitHub Actionsがデプロイ用に3種類のSVGを再生成し、続けてGitHub Pagesをビルドします。ただし、Actionsが生成したSVGはリポジトリへ書き戻しません。

cloneした環境のMarkdownプレビューにも変更を反映するには、ソースと生成後のSVGを同じコミットに含めてください。

### ローカルで更新する

LilyPondをインストールしている場合、楽譜は次のコマンドで更新できます。

```bash
lilypond --svg -dno-point-and-click \
  --output=assets/generated/score music/example.ly
```

MermaidとPlantUMLは、現在のGitHub Actionsと同じKroki APIを使って更新できます。

```bash
curl --fail --header "Content-Type: text/plain" \
  --data-binary @diagrams/solution-flow.mmd \
  https://kroki.io/mermaid/svg \
  --output assets/generated/mermaid.svg

curl --fail --header "Content-Type: text/plain" \
  --data-binary @diagrams/solver-sequence.puml \
  https://kroki.io/plantuml/svg \
  --output assets/generated/plantuml.svg
```

Krokiを使う場合、図のソースは外部サービスへ送信されます。機密情報を含む図では、ローカルにMermaid CLIやPlantUMLを導入してSVGを生成してください。

## HTMLへのコンパイル

1. VS CodeでコンパイルするMarkdownファイルを開きます。
2. コマンドパレットを開きます。
3. `Marp: Export Slide Deck` を実行します。
4. 保存先を指定します。

このリポジトリでは出力形式をHTMLに設定しているため、同じディレクトリにHTMLファイルが生成されます。

## GitHub Pagesへの公開

`main` ブランチへ変更をpushすると、GitHub Actionsが `template.md` を `index.html` に変換してGitHub Pagesへ公開します。

初回のみ、GitHubリポジトリの `Settings` → `Pages` → `Build and deployment` で、`Source` を `GitHub Actions` に設定してください。その後、`Actions` タブの `Deploy Marp to GitHub Pages` が完了すると公開URLへアクセスできます。
