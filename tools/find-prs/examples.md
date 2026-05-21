# find-prs 使用例

## 例 1: 既定設定（oneline + 自動コピー）

入力：
```
/find-prs 1234
```

出力：
```
mall4最新(#12), mall3最新(#34), release-2024(#11), release-2025(#13)

4 件ヒット
oneline をクリップボードへコピーしました
```

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

mall4最新(#12), mall3最新(#34), release-2025(#13)

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
| 仓储:分支 | PR# | State | Title | URL |
|----------|-----|-------|-------|-----|
| mall4:develop | #12 | merged | 1234 患者一覧の検索条件修正 | https://github.com/medley-inc/mall4/pull/12 |
| mall4:release-2025 | #13 | merged | 1234 患者一覧の検索条件修正 | https://github.com/medley-inc/mall4/pull/13 |

2 件ヒット
コピー対象（oneline）が出力に含まれないためスキップしました
```

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
