---
name: find-prs
description: Use when the user invokes /find-prs to search PRs by title across all repositories in a GitHub organization. Outputs results in oneline / tree / table formats and optionally copies the oneline form to the clipboard.
---

# find-prs

## Overview

GitHub 組織配下の全リポジトリから、PR タイトルにキーワードを含む PR を一括検索し、oneline・tree・table の 3 形式で結果を整形して出力するスラッシュコマンド。oneline は Windows 環境で自動的にクリップボードへコピーされ、Excel / Kintone 等への貼り付けを容易にする。

あなたは、複数の長期ブランチをまたぐ同一要件の修正状況を集計するアシスタントです。検索 → 集計 → 整形を機械的に正確に実行してください。

## Usage

```
/find-prs <keyword> [--org <name>] [--state <s>] [--format <f>] [--copy|--no-copy]
```

### 引数・オプション

| 名前 | 必須 | デフォルト | 値域 | 説明 |
|------|------|-----------|------|------|
| `<keyword>` | はい | — | 任意文字列 | PR タイトル検索キーワード（例: `1234`、`患者一覧`） |
| `--org` | いいえ | `medley-inc` | 任意組織名 | GitHub 組織名 |
| `--state` | いいえ | `all` | `open` / `closed` / `merged` / `all` | PR 状態フィルタ |
| `--format` | いいえ | `table` | `oneline` / `tree` / `table`、カンマ区切り複数指定可 | 出力形式 |
| `--copy` / `--no-copy` | いいえ | `--no-copy` | フラグ | `--copy` 明示指定時のみ oneline をクリップボードへコピー（Windows のみ有効） |

呼び出し例：

```
/find-prs 1234
/find-prs 1234 --state merged --format tree,oneline
/find-prs 患者一覧 --format table
/find-prs 1234 --org medley-inc --format tree,table,oneline --no-copy
```

---

## Step 1: 前提チェック

`gh auth status` を実行し、認証されていなければ「`gh auth login` を実行してください」と告知し中断する。

プラットフォームを判定する（Windows / macOS / Linux）。クリップボード処理の分岐に使う。

---

## Step 2: 引数パース

ユーザー入力から `<keyword>` と各オプションを抽出する。

- `<keyword>` は最初の位置引数。空ならエラー「キーワードを指定してください」で中断
- `--org` 未指定なら `medley-inc`
- `--state` 未指定なら `all`
- `--format` 未指定なら `table`。カンマ区切りなら配列化（例: `tree,oneline` → `["tree","oneline"]`）。不正な値があれば中断
- `--copy` / `--no-copy` 未指定なら `--no-copy`（既定はコピーしない）

---

## Step 3: PR を検索

`gh search prs` で組織横断検索を実行する。

```
gh search prs --owner <org> "<keyword>" --match title \
  [状態フラグ] \
  --json number,title,repository,state,url --limit 100
```

**状態フラグのマッピング：**

| `--state` | `gh search prs` への渡し方 |
|-----------|---------------------------|
| `open` | `--state open` |
| `closed` | `--state closed` |
| `merged` | `--merged`（`--state merged` は不可） |
| `all` | フラグ未指定（既定動作） |

**結果ハンドリング：**

- 結果 0 件 → 「指定キーワードに一致する PR が見つかりませんでした」と出力して正常終了
- 結果が 100 件ちょうど → 「結果が上限 100 件で切り捨てられている可能性があります。より具体的なキーワードをご検討ください」と末尾に警告

---

## Step 4: base 分支を補完

`gh search prs` の JSON 出力には `baseRefName` が含まれない。各 PR について追加取得する：

```
gh pr view <number> --repo <owner/repo> --json baseRefName
```

複数の `gh pr view` 呼び出しは **1 メッセージ内で並列実行**してレイテンシを下げる。

個別の `gh pr view` 失敗時は、当該 PR をスキップして警告ログを残し、他の PR の処理を継続する。

---

## Step 5: 集計・並び替え

検索結果を `repository.nameWithOwner` で groupBy する。**oneline・tree・table すべて同じ repo グループ順序**で出力する。

**repo グループの並び順（medley-inc 既定の優先順位）：**

1. `mall4`
2. `mall3`
3. `mall-jinei`
4. その他の repo（辞書順）

`--org` が `medley-inc` 以外の場合は上記優先リストを無視し、全 repo を辞書順とする。

**各 repo グループ内の並び順（全形式共通）：**

1. `baseRefName == "develop"` の条目を先頭
2. その後、他の分支条目を分支名の辞書順

**同一 repo・同一 base 分支に複数 PR が存在する場合：**

各 PR を独立した条目として全て出力する（集約しない）。oneline では同一表記が複数回現れる可能性がある（例: `mall4最新(#12), mall4最新(#15)`）。

---

## Step 6: 整形出力

`--format` で指定された形式を **指定順** に出力する。形式間は空行 1 行で区切る。

### 6.1 oneline 形式

ルール：
- `baseRefName == "develop"` → `<repo>最新(#PR番号)`
- それ以外 → `<分支名>(#PR番号)`
- 区切り: `, `（半角カンマ + 半角スペース）
- repo グループ単位で連続させる（Step 5 の並び順）。mall4 のすべての条目を出し切ってから mall3 に移る、というように **repo を跨いで develop だけまとめて先頭に出すことはしない**

例（mall4 に develop + 1 release、mall3 に develop の場合）：

```
mall4最新(#12), release-2025(#13), mall3最新(#34)
```

### 6.2 tree 形式

ルール：
- 行頭に repo 名のみ（組織名なし）
- 次行から半角スペース 2 個でインデント、ツリー記号なし
- 各エントリは `<分支名>: <URL>`
- 複数 repo 間に空行を入れない（密に詰める）

例：

```
mall4
  develop: https://github.com/medley-inc/mall4/pull/12
  release-2025: https://github.com/medley-inc/mall4/pull/13
mall3
  develop: https://github.com/medley-inc/mall3/pull/34
```

### 6.3 table 形式

Markdown 表形式。**共通プレフィックス集約後のタイトル残り件数で列構成を切り替える**：

| 集約後の件数 | 列構成 | テーブル直前の Title 表示 |
|-------------|--------|--------------------------|
| **1 件**（共通プレフィックスで集約可能＝末尾サフィックスだけが違うケース） | `ブランチ \| PR# \| State \| URL`（Title 列なし） | `**Title:** <タイトル>` を 1 行表示 |
| **2 件以上**（明らかに異なるタイトルが共存するケース） | `ブランチ \| PR# \| State \| Title \| URL`（Title 列あり） | 出さない |

**共通プレフィックス集約ルール：**

タイトル A が別タイトル B の **完全な前方一致プレフィックス**である場合、より長い B は非表示にし、最短の A だけ残す。中間一致・部分一致では集約しない（誤集約を避けるため）。

**列セルの内容：**

- `ブランチ`：`<repo>:<分支名>`（develop の簡略化なし）
- `PR#`：`#<番号>`
- `State`：`open` / `closed` / `merged`
- `Title`（2 件以上のときのみ存在）：PR タイトル原文
- `URL`：PR の HTML URL

例 A（集約後 1 件）：

**Title:** 1234 患者一覧の検索条件修正

| ブランチ | PR# | State | URL |
|---------|-----|-------|-----|
| mall4:develop | #12 | merged | https://github.com/medley-inc/mall4/pull/12 |
| mall4:release-2025 | #13 | merged | https://github.com/medley-inc/mall4/pull/13 |

例 B（集約後 2 件以上）：

| ブランチ | PR# | State | Title | URL |
|---------|-----|-------|-------|-----|
| mall4:develop | #20 | merged | 5678 在庫一覧の表示崩れ修正 | https://github.com/medley-inc/mall4/pull/20 |
| mall3:develop | #45 | merged | 9012 予約画面のバリデーション追加 | https://github.com/medley-inc/mall3/pull/45 |

---

## Step 7: クリップボード反映

クリップボードコピーは **`--copy` が明示指定されたとき限定**。未指定 / `--no-copy` の場合は何もせず、完了報告にも何も出さない。

以下の全条件を満たす場合のみ実行する：

- `--copy` が明示指定されている
- プラットフォームが Windows
- `--format` に `oneline` が含まれる

実行コマンド：

```powershell
Set-Clipboard -Value "<oneline 出力>"
```

**スキップ条件（`--copy` 明示指定時のみ告知）：**

| 状況 | 動作 |
|------|------|
| `--copy` 未指定 / `--no-copy` | スキップ（告知不要、Step 8 でも触れない） |
| Windows 以外（`--copy` 指定時） | スキップし、完了報告で「macOS/Linux ではクリップボード未対応のためスキップしました」と告知 |
| `--format` に oneline 未含有（`--copy` 指定時） | スキップし、完了報告で「コピー対象（oneline）が出力に含まれないためスキップしました」と告知 |

---

## Step 8: 完了報告

以下を末尾に出力する。クリップボードに関する告知も**ここで一括して行い、Step 7 では出力しない**。

- ヒット件数（例: 「3 件ヒット」）
- 100 件警告（該当時、Step 3 で検知）
- クリップボード結果は **`--copy` が明示指定されたときのみ** 1 行出力する：
  - 成功時: 「oneline をクリップボードへコピーしました」
  - Windows 以外の場合: 「macOS/Linux ではクリップボード未対応のためスキップしました」
  - `--format` に oneline 未含有の場合: 「コピー対象（oneline）が出力に含まれないためスキップしました」

`--copy` 未指定 / `--no-copy` の場合は、クリップボードに関する行は **出力しない**（無音）。

---

## 参考：gh コマンド一覧

```bash
# 認証チェック
gh auth status

# PR 検索（全状態）
gh search prs --owner medley-inc "1234" --match title \
  --json number,title,repository,state,url --limit 100

# PR 検索（merged のみ）
gh search prs --owner medley-inc "1234" --match title --merged \
  --json number,title,repository,state,url --limit 100

# base 分支の取得
gh pr view 12 --repo medley-inc/mall4 --json baseRefName
```
