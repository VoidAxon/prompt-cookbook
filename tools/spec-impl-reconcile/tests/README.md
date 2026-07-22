# RED-GREEN 回帰フィクスチャ（spec-impl-reconcile）

スキル（SKILL.md / references / scripts）を編集したら、退行していないかをここで再確認する。
writing-skills の RED-GREEN 準拠。DESIGN の検証記録は文章だったが、以後はこの手順で実測する。

## フィクスチャ
- `fixture/spec/OrderEntry.md` … AI生成想定のダミー設計書。わざと欠陥を仕込んである。
- `fixture/impl/OrderEntryForm.cs` … 実装側の"事実"。設計書とわざと食い違わせてある。

## 仕込んだ欠陥（GREEN が検出すべきもの）
| 期待 | 内容 |
|---|---|
| 実在ゲート → **B・高・再抽出** | 設計書の中核 `OrderService.ExecuteOrder()`／`IOrderRepository` が実装に0件。実体は `Execute(typeof(CommonQuery_Order))` 直呼び＝「帰属先の誤り」を記録 |
| **A2・高・横断新設** | 保存後の外部在庫送信 `InventoryNotifier.Send` が設計書に無い（効果が本画面の外へ波及） |
| **A1・新規抽出** | 確認子画面 `OrderConfirmDialog`（`ShowDialog`／明細削除機能あり）が設計書に無い |
| **再報しない**（スコープ／既知） | 空catch `PrintReceipt` はバグ候補#1に既記載。E に上げ直さず確認済みメモに留める |
| 出力規律 | ①〜④構造で出力し、③が `../scripts/pipe_to_xlsx.py` で **exit 0** |

## 回し方
1. **RED（skill無し）**: `fixture/` を素の状態で突合させ、上の検出・出力規律が"欠ける"ことを確認（ベースライン。特に空catchをバグとして起票しがち・幻覚を素通ししがち）。
2. **GREEN（skill有り）**: `/spec-impl-reconcile fixture/spec/OrderEntry.md OrderEntryForm` 相当で回し、上表を全て満たすことを確認。
3. 汚染を避けるため独立サブエージェントで回すと再現性が高い（writing-skills 準拠）。

## ③ の機械チェック（脚本）だけ単体で回す例
③のパイプ表を書き出してスクリプトへ通し、exit 0 を確認する（受控列 `分類`/`深刻度`/`対処区分` は既定で照合される）:

```
python ../scripts/pipe_to_xlsx.py <③を書き出したファイル> /tmp/orderentry_issues
# 指摘箇所も照合したいなら（この設計書テンプレートのセクション名を渡す）:
python ../scripts/pipe_to_xlsx.py <③> /tmp/orderentry_issues \
    --sections "概要,入力,出力,トリガー,外部連携,バグ候補"
```

## 合格条件
上表の5項目すべて。特に退行しやすいのは次の2点:
- **空catch を新規バグとして起票しない**（バグ狩りへの漂流防止）。
- **ハルシネーションを"帰属先の誤り"付きで B・高・再抽出**（実在ゲートの早期検出）。
