# aizome

Marp用のカスタムテーマです。

著者: [github.com/ymho](https://github.com/ymho)

スライドの記述例と利用できるレイアウトは [templates.md](./templates.md) を参照してください。

## 必要なもの

- [Visual Studio Code](https://code.visualstudio.com/)
- VS Code拡張機能 [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode)

VS Codeの拡張機能ビューを開き、`Marp for VS Code` を検索してインストールしてください。

## 開き方

このリポジトリをクローンまたはダウンロードし、VS Codeでフォルダ全体を開きます。`templates.md` だけを単独で開くとカスタムテーマの設定が読み込まれないため、必ずフォルダ、または `marp-aizome.code-workspace` を開いてください。

ワークスペースの信頼を求められた場合は、内容を確認したうえで信頼済みにします。制限モードではカスタムCSSが読み込まれないことがあります。

## プレビュー

1. VS Codeで `templates.md` を開きます。
2. `Ctrl+K`、続けて `V` を押します。macOSでは `⌘+K`、続けて `V` を押します。

コマンドパレットから開く場合は、`Markdown: Open Preview to the Side` を実行します。エディター右上のプレビューアイコンから開くこともできます。

Marp専用のプレビューコマンドではなく、VS Code標準のMarkdownプレビューを使用します。`Marp for VS Code` がインストールされ、Markdown先頭に `marp: true` があれば、スライドとして表示されます。

## HTMLへのコンパイル

1. VS CodeでコンパイルするMarkdownファイルを開きます。
2. コマンドパレットを開きます。
3. `Marp: Export Slide Deck` を実行します。
4. 保存先を指定します。

このリポジトリでは出力形式をHTMLに設定しているため、同じディレクトリにHTMLファイルが生成されます。

新しいスライドを作る場合は、`templates.md` をコピーして編集してください。先頭のFront Matterには次の指定が必要です。

```yaml
---
marp: true
theme: aizome
paginate: true
size: 16:9
---
```

## GitHub Pagesへの公開

`main` ブランチへ変更をpushすると、GitHub Actionsが `templates.md` を `index.html` に変換してGitHub Pagesへ公開します。

初回のみ、GitHubリポジトリの `Settings` → `Pages` → `Build and deployment` で、`Source` を `GitHub Actions` に設定してください。その後、`Actions` タブの `Deploy Marp to GitHub Pages` が完了すると公開URLへアクセスできます。
