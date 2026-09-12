# AI Agent向けの確認・配布ツール

編集・プレビューに新しい環境を必須として追加するものではありません。Python 3.10以上がある場合は静的確認とZIP作成を追加パッケージなしで利用できます。ブラウザでの確認は開発者ツールでも実行でき、CIや既存の自動化環境ではNode.jsの入口も使えます。

## 1. レイアウト契約

[ai/layouts.json](../ai/layouts.json) がAI向けの設定一覧です。[JSON Schema](../ai/layouts.schema.json)も同梱しています。

- `layouts`：用途、必要なMarkdown構造、項目数の目安、項目数による配置。
- `modifiers`：同時指定できないグループ、必要な基本レイアウト、避ける組み合わせ。
- `deprecated`：旧クラスと移行先。
- `rules`：タイトル・出典・参照などの共通条件。

`schemaVersion` は形式のバージョン、`version` はこの契約を提供するテーマのバージョンです。独自テーマのクラスを勝手に推測せず、未知の設定はCSSと実際の表示を確認します。CSS・READMEの仕様を変えるときは、この契約も一緒に更新してください。

### 共通の色定義

色の原本は [ai/colors.json](../ai/colors.json) です。配色名は日本語、指定名はローマ字で、本文・図表・コード・注釈・蛍光ペンが同じ値を参照します。

```bash
python3 tools/sync_colors.py
python3 tools/sync_colors.py --check
```

最初のコマンドはCSS内の管理ブロックを更新し、`--check` は定義が一致していなければ終了コード1にします。生成後のCSSをコミットするので、利用者が編集・表示する際に変換処理を追加する必要はありません。手書きのコンポーネントCSSに色コードを足さず、役割別の変数を利用します。

## 2. 静的チェック

リポジトリ直下で実行します。WindowsのPython Launcherでは `python3` を `py -3` に置き換えられます。

```bash
python3 tools/check_slides.py template.md
python3 tools/check_slides.py template.md --json
python3 tools/check_slides.py template.md --strict
```

終了コードは0＝エラーなし、1＝内容の問題、2＝ファイル読み込み・実行条件の問題です。`--strict` は警告も1にします。JSONは `schemaVersion`、`scope`、`slides`、`errors`、`warnings`、`findings` を返します。各指摘には `severity`、`code`、`slide`、`message` が入ります。

廃止クラス、設定の衝突、リスト構造、項目数、注釈・出典、HTMLタグ、ローカル画像・ファイル、ページ参照、重複した図表名を確認します。コードフェンス内の説明例は対象外です。パスはMarkdownファイルからの相対位置で確認します。

**Markdownの完全なパーサーではありません。** 標準のインラインリンク・参照形式画像と、カタログで使うローカルディレクティブを対象にしています。複雑なURLや記法、YAMLの高度な構文、グローバルな `class` 継承、独自Markdownプラグインは完全には評価しません。未知のクラスと、静的に解決できない見出しリンクは警告にします。文章の正しさ、実際の改行、図の読める大きさは別に確認してください。

## 3. 表示チェック（ブラウザだけでも可能）

1. Marpで書き出したHTMLをブラウザで開く。
2. 開発者ツールのConsoleで [check-rendered.js](check-rendered.js) の内容を実行する。
3. `await aizomeCheck()` を実行する。

フォント3ウェイト、画像読み込み、スライドからのはみ出し、コードの切れ、タイトル・本文・出典の重なり、ページ内リンクを確認し、JSONを返します。処理中は各スライドへ移動し、最後に元の位置へ戻ります。画像の読み込みには最大8秒待ちます。回線が遅い場合は `await aizomeCheck({timeoutMs: 20000})` として再確認できます。

フォントを正常に読み込めても、各OSの描画まで完全一致する保証はありません。画像内の小さな文字や意味上の読みやすさは画面でも確認します。

### Node.jsの既存環境を使う場合

Node.js 22、`puppeteer-core`、Chromium/Chromeが利用可能なら、次で自動化できます。利用者全員に導入を求める必要はありません。CIはこの方法で実行します。

```bash
node tools/check-browser.cjs presentation.html \
  --root . \
  --browser /path/to/chrome \
  --module /path/to/node_modules/puppeteer-core \
  --output /tmp/aizome-report.json \
  --screenshots /tmp/aizome-screenshots
```

`--root` はHTML内の画像・フォントURLの基準フォルダで、標準はHTMLのある場所です。検証用のHTTPサーバーを127.0.0.1の一時ポートで開き、完了時に閉じます。HTMLを `/tmp` に書き出し、素材をリポジトリに置いたまま確認するときは `--root .` を使えます。任意のフォルダ構造を自動で修復するものではありません。

実行環境の制約で必要な場合だけ `--no-sandbox` を指定できます。JSONのエラーがあれば終了コード1、実行環境などの失敗は2です。`--screenshots` は任意で、全スライドのPNGを保存します。デッキ自体へ検証コードを埋め込む必要はありません。

## 4. 配布用ZIPを作る

先に、利用可能なVS Code拡張またはCLIでHTMLを書き出します。その後、次を実行します。

```bash
python3 tools/package_slides.py presentation.html dist/presentation.zip
```

HTMLを別フォルダへ出力した場合の例：

```bash
python3 tools/package_slides.py /tmp/presentation.html dist/presentation.zip --root .
```

ZIPには `index.html`、参照されたローカル画像・フォント・CSS・スクリプト、同梱フォントのライセンス、`README.txt`、`manifest.json` が入ります。衝突しないファイル名へ変更してHTML/CSSの参照先も書き換えるため、別PCへフォルダごと渡せます。`manifest.json` には同梱ファイルのSHA-256、外部リソース、同梱しなかったローカル文書リンクを記録します。同じ入力なら同じZIPになります。

- 出力先のZIPが既にあれば停止します。上書きする場合は、不要であることを確認してから別途削除するか、別名を指定します。
- `--root` の外やシンボリックリンク経由で外へ出るリソースは同梱しません。欠けた素材はエラーにします。
- 外部素材は勝手にダウンロードしません。絵文字などが外部URLのままなら、閲覧時もネット接続が必要です。
- 通常のリンク先にあるローカル文書は自動同梱しません。個別資料まで意図せず配布しないためです。必要なら別途共有します。
- 外部CSS・JavaScript内部の動的な通信は検出対象外です。外部依存0件の表示だけで完全オフラインを保証しません。
- `<base>`、`srcset`、内部から外部ファイルを参照するSVGは事前の整理が必要です。エラー時は設定や素材を確認し、検出を無効にして進めないでください。

ZIPは全部展開し、`index.html` を開きます。ブラウザのローカルファイル制限がある場合は、展開先で `python3 -m http.server 8000 --bind 127.0.0.1` を起動して確認できます。**元の作業フォルダではなく、展開先で表示チェックを行う**ことで素材の入れ忘れを確認します。

## 5. 改善例とCI

[改善例](../examples/repairs.md)に、意図的に問題を含むMarkdownと修正後のMarkdown、直した理由をまとめています。修正前の失敗はテストで期待される結果です。

```bash
python3 -m unittest discover -s tests -v
```

PRのCIでは、静的チェック、テスト、HTML生成、表示チェック、ZIP作成、展開後の表示チェックを実施します。チェック結果と配布ZIPをActionsのartifactに保存します。スライドの元データを外部の生成サービスに送る必要はありません。

全体配色の選択肢は `ai/themes.json`、対応CSSは `themes/` です。`sync_colors.py` はベースCSSの色と派生テーマCSSの両方を同期し、`--check` でも確認します。Marp CLIには `--theme-set aizome.css themes/*.css` を指定します。
