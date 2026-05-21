# find-prs 使用例

## 例 1: 既定設定（oneline + 自動コピー）

入力：
```
/find-prs 1234
```

出力：
```
mall4最新(#12), release-2025(#13), mall3最新(#34), release-m3-2025.08.31(#256)

4 件ヒット
oneline をクリップボードへコピーしました
```

repo 優先順位（mall4 → mall3 → mall-jinei → その他）に沿って repo グループ単位で連続出力される。各 repo 内では develop が先、他分支は分支名辞書順。

## 例 2: tree + oneline 併用（merged のみ）

入力：
```
/find-prs 1234 --format tree,oneline --state merged
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

## 例 3: table 単独

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
コピー対象（oneline）が出力に含まれないためスキップしました
```

複数のタイトルがある場合は `**Titles:**` 見出しに切り替わり、共通プレフィックスを持つタイトル群は最短のもの 1 つに集約される。

## 例 4: 0 件ヒット

入力：
```
/find-prs 存在しないキーワード
```

出力：
```
指定キーワードに一致する PR が見つかりませんでした
```

## 例 5: 100 件上限警告

入力：
```
/find-prs fix
```

出力（抜粋）：
```
fix(#1), fix(#2), ..., fix(#100)

100 件ヒット
結果が上限 100 件で切り捨てられている可能性があります。より具体的なキーワードをご検討ください
oneline をクリップボードへコピーしました
```
