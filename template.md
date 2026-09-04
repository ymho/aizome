---
marp: true
theme: aizome
paginate: true
size: 16:9
title: Aizome — Marp presentation template
author: Your Name
---
<!-- _class: cover -->

# Aizome

## 伝えたいことを、静かに強く。

Marp presentation template / Your Name

---
<!-- _class: agenda -->

# このテンプレートでできること

1. メッセージを一枚で立てる
2. 情報を比較・整理する
3. プロセスや数字を見せる
4. 技術情報とビジュアルを扱う

---
<!-- _class: section -->

# 01. Message

## まず、聞き手に残したい一文を決める

---
<!-- _class: statement -->

# 一番伝えたいこと

**資料の価値は、情報量ではなく「見え方が変わること」で決まる。**

補足はこの下に短く置きます。本文を増やすより、主張を一つに絞るスライドです。

---

# 標準スライド

本文スライドは、タイトルとコンテンツの境界を明確にしています。

- 1スライド1メッセージを基本にする
- 箇条書きは3〜5点程度に抑える
- **重要語だけを太字**にして視線を誘導する
- 詳細は表・図・Appendixへ逃がす

> 補足や「ここだけ覚えてほしい」内容は、引用記法でコールアウトにできます。

---
<!-- _class: cards -->

# 3つの論点を並べる

- **Why**
  なぜ今、このテーマに取り組むのか。

- **What**
  何を変え、何を変えないのか。

- **How**
  どう進め、どう確かめるのか。

---
<!-- _class: section -->

# 02. Structure

## 比較・整理・意思決定を一目で伝える

---
<!-- _class: compare -->

# Before / After

- **Before｜任せる**
  - 選択肢は誰かが決める
  - 理由は後から説明される
  - レビューは正解探しになりやすい

- **After｜自分で選ぶ**
  - 自分で選ぶ
  - 自分で説明する
  - 自分でレビューする

---
<!-- _class: columns -->

# 2カラムで整理する

- **変えないもの**
  - 安全性
  - 信頼性
  - 説明責任

- **変えるもの**
  - 意思決定の速度
  - 検証の粒度
  - 学習のサイクル

---
<!-- _class: decision -->

# 意思決定を明示する

背景と選択肢を説明したあと、最後に結論だけを独立させます。

> **Decision:** 小さく作って検証し、成立条件が見えたものから本番へ広げる。

このレイアウトは会議資料・設計レビュー・提案資料で使いやすい構成です。

---
<!-- _class: table-center -->

# 表は比較軸を揃える

| 観点 | 案A | 案B | 判断 |
|---|---|---|---|
| 初期コスト | 小 | 中 | A |
| 拡張性 | 中 | 大 | B |
| 運用負荷 | 小 | 中 | A |
| 将来性 | 中 | 大 | B |

---
<!-- _class: section -->

# 03. Flow & Metrics

## 流れと数字は、文章より構造で見せる

---
<!-- _class: process -->

# 4ステップのプロセス

1. **Observe**
   現状を見る
2. **Choose**
   選択する
3. **Build**
   小さく作る
4. **Learn**
   結果から学ぶ

---
<!-- _class: kpi -->

# 数字を主役にする

- **42%**
  *削減率*
  手作業の削減

- **3.2x**
  *速度*
  検証サイクル

- **12→4**
  *工程数*
  承認ポイント

- **99.9%**
  *SLO*
  目標可用性

---
<!-- _class: roadmap -->

# ロードマップ

1. **Explore**
   課題と仮説を整理
2. **Prototype**
   最小構成で試す
3. **Validate**
   数字と現場で確認
4. **Scale**
   本番へ展開

---
<!-- _class: quote -->

# 引用・キーメッセージ

> 完璧な計画より、検証できる小さな一歩を増やす。

— Aizome sample

---
<!-- _class: section -->

# 04. Technical

## コード・図・画像も同じトーンで扱う

---

# コードを見せる

```typescript
export async function decide(input: Context) {
  const options = await explore(input)
  const choice = rank(options)[0]

  return {
    choice,
    reason: explain(choice),
  }
}
```

コード面は藍色のダークサーフェスにして、本文との差を明確にしています。

---
<!-- _class: image-right -->
![bg right:50% 45%](assets/generated/mermaid.svg)

# 図と説明を半分ずつ

図を右、文章を左に置くレイアウトです。

- 図の意味をタイトルで先に言い切る
- 本文は「図の読み方」に集中する
- `right` を `left` に変えれば左右反転できます

---
<!-- _class: image-left -->
![bg left:50% cover](assets/placeholder-map.svg)

# 画像を左に置く

背景画像を使う場合も、文章領域へ重ならないように余白を確保しています。

> 写真・地図・UIキャプチャと相性の良いレイアウトです。

---
<!-- _class: full-image -->
![bg cover brightness:0.62](assets/placeholder-rail.svg)

# ビジュアルを主役にする

文章は結論だけに絞る。

---
<!-- _class: section -->

# Appendix

## 補足・注意・密度の高い情報

---
<!-- _class: success -->

# Success callout

> **成立条件:** 主要な利用シナリオで期待値を満たし、運用手順まで確認できた。

通常の本文と区別して、確認済みの事実や完了条件を示せます。

---
<!-- _class: warning -->

# Warning callout

> **注意:** 外部サービスへ送信するデータに機密情報が含まれないことを確認する。

注意事項は黄色系のアクセントに切り替えられます。

---
<!-- _class: dense -->

# Dense / Appendix

密度の高い情報は `dense` クラスへ逃がします。本文で無理に小さな文字を使わないことが重要です。

| 項目 | 内容 | 備考 |
|---|---|---|
| Theme | `aizome` | `aizome.css` |
| Ratio | 16:9 | 標準 |
| Export | HTML / PDF / PPTX | Marp CLI / VS Code |
| Layout | class指定 | HTMLを書かずに利用可能 |

```yaml
---
marp: true
theme: aizome
paginate: true
size: 16:9
---
```

---
<!-- _class: profile -->

# Profile

![avatar w:220px](./assets/profile-placeholder.svg)

## Your Name
Product / Engineering / Design

- **Role**：役割や専門領域
- **Focus**：今取り組んでいるテーマ
- **Message**：今日伝えたいこと

> 一言で覚えてもらえる自己紹介を置きます。

[![sns-github w:60px](./assets/icons/GitHub_Invertocat_Black_Clearspace.svg)](https://github.com/)

---
<!-- _class: closing -->

# Thank you

伝えたいことを、静かに強く。
