# 注文入力（OrderEntry）  ＜テスト用フィクスチャ・AI生成想定の設計書＞

> これは spec-impl-reconcile の RED-GREEN 回帰用ダミー設計書。
> わざと ①ハルシネーション（実在しない中核層）②横断欠落 ③子画面欠落 を仕込み、
> かつ既知バグを「バグ候補」に載せてある（＝レビューで再報されないことの確認用）。
> 実装側の"事実"は `../impl/OrderEntryForm.cs`。

## ソース（実在確認済）
- `OrderService.ExecuteOrder()` … 注文確定の中核メソッド
- `IOrderRepository.Save()` … 永続化層

（※上の2つは実装に存在しない。実体は `OrderEntryForm` が `Execute(typeof(CommonQuery_Order))` を
直呼びする旧構造。実在ゲートで **B・高・再抽出**、かつ「帰属先の誤り」の記録になるべき。）

## 概要
注文入力画面。保存ボタンで注文を確定し、`OrderService.ExecuteOrder()` が
`IOrderRepository` を通じて注文を永続化する。

## 入力
- 注文ID、注文明細

## 出力
- 保存完了メッセージ、レシート印刷

## トリガー
- 保存ボタン `btnSave_Click`

## 外部連携
- （記載なし）

（※実装は保存後に外部在庫システムへ `InventoryNotifier.Send` で送信している。
効果が本画面の外へ波及するので **A2・高・横断新設** になるべき。）

## バグ候補
- #1 レシート印刷 `PrintReceipt` の例外を空catchで握り潰しており、失敗が無通知。

（※#1 は既知として記載済み。レビューで新規バグとして再報せず、確認済みメモに留めること。）
