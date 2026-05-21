# find-prs 使用例

## 例 1: 既定設定（table 単独、クリップボードコピー無し）

入力：
```
/find-prs 1234
```

出力：
```
**Title:** 1234 患者一覧の検索条件修正

| ブランチ | PR# | State | URL |
|---------|-----|-------|-----|
| mall4:develop | #12 | merged | https://github.com/medley-inc/mall4/pull/12 |
| mall4:release-2025 | #13 | merged | https://github.com/medley-inc/mall4/pull/13 |
| mall3:develop | #34 | merged | https://github.com/medley-inc/mall3/pull/34 |
| mall3:release-m3-2025.08.31 | #256 | merged | https://github.com/medley-inc/mall3/pull/256 |

4 件ヒット
```

`--format` 既定は `table`、`--copy` も既定 OFF。クリップボードへコピーしたい場合は `--format oneline --copy` または `--format table,oneline --copy` のように明示指定する。

## 例 2: tree + oneline 併用（merged のみ、`--copy` 明示）

入力：
```
/find-prs 1234 --format tree,oneline --state merged --copy
```

出力：
```
mall4
  develop: https://github.com/medley-inc/mall4/pull/12
  release-2025: https://github.com/medley-inc/mall4/pull/13
mall3
  develop: https://github.com/medley-inc/mall3/pull/34

mall4最新(#12), release-2025(#13), mall3最新(#34)

3 件ヒット
oneline をクリップボードへコピーしました
```

`--copy` を明示した時のみクリップボードコピーが行われ、完了報告にその結果が出力される。

## 例 3: table 単独（集約後 1 件 — 共通プレフィックスのケース）

入力：
```
/find-prs 患者一覧 --format table
```

出力：
```
**Title:** 1234 患者一覧の検索条件修正

| ブランチ | PR# | State | URL |
|---------|-----|-------|-----|
| mall4:develop | #12 | merged | https://github.com/medley-inc/mall4/pull/12 |
| mall4:release-2025 | #13 | merged | https://github.com/medley-inc/mall4/pull/13 |

2 件ヒット
```

タイトルが共通プレフィックスで 1 つに集約できる場合は **Title 列を削除**し、テーブルの直前に `**Title:**` を 1 行で表示する。

## 例 4: table 単独（集約後 2 件以上 — 異なるタイトル共存ケース）

入力：
```
/find-prs バリデーション --format table
```

出力：
```
| ブランチ | PR# | State | Title | URL |
|---------|-----|-------|-------|-----|
| mall4:develop | #20 | merged | 5678 在庫画面のバリデーション緩和 | https://github.com/medley-inc/mall4/pull/20 |
| mall3:develop | #45 | merged | 9012 予約画面のバリデーション追加 | https://github.com/medley-inc/mall3/pull/45 |

2 件ヒット
```

タイトルが共通プレフィックスで集約できず複数残る場合は **Title 列を表内に保持**し、テーブル直前の Title 行は出さない。

## 例 5: 0 件ヒット

入力：
```
/find-prs 存在しないキーワード
```

出力：
```
指定キーワードに一致する PR が見つかりませんでした
```

## 例 6: 100 件上限警告（`--format oneline --copy` 指定）

入力：
```
/find-prs fix --format oneline --copy
```

出力（抜粋）：
```
fix(#1), fix(#2), ..., fix(#100)

100 件ヒット
結果が上限 100 件で切り捨てられている可能性があります。より具体的なキーワードをご検討ください
oneline をクリップボードへコピーしました
```

100 件で結果が切り捨てられる可能性がある場合、件数行の次にこの警告を出す。クリップボード関連の行は `--copy` 明示時のみ表示される。
