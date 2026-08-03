# aizome

Marp用のカスタムテーマです。

スライドの記述例と利用できるレイアウトは [template.md](./template.md) を参照してください。

## Slides

- `transitforge.md`: TransitForgeの構築・運用・改善の取り組み
- `template.md`: aizomeテーマのレイアウトサンプル
- `aizome.css`: 共通テーマ（図版、スクリーンショット、フローを含む）

GitHub Pagesのトップでは`transitforge.md`を表示し、テーマ見本は
`template.html`として同時に出力します。

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

コマンドパレットから開く場合は、`Markdown: Open Preview to the Side` を実行します。エディター右上のプレビューアイコンから開くこともできます。

Marp専用のプレビューコマンドではなく、VS Code標準のMarkdownプレビューを使用します。`Marp for VS Code` がインストールされ、Markdown先頭に `marp: true` があれば、スライドとして表示されます。

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

新しいスライドを作る場合は、`template.md` をコピーして編集してください。先頭のFront Matterには次の指定が必要です。

```yaml
---
marp: true
theme: aizome
paginate: true
size: 16:9
---
```

## GitHub Pagesへの公開

`main` ブランチへ変更をpushすると、GitHub Actionsが `transitforge.md` を `index.html` に変換してGitHub Pagesへ公開します。テーマ見本の `template.md` も `template.html` として同時に出力します。

初回のみ、GitHubリポジトリの `Settings` → `Pages` → `Build and deployment` で、`Source` を `GitHub Actions` に設定してください。その後、`Actions` タブの `Deploy Marp to GitHub Pages` が完了すると公開URLへアクセスできます。
