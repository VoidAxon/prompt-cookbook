# find-prs 设计文档

作成日: 2026-05-21
ステータス: ドラフト
スキル種別: スラッシュコマンド（Claude Code 用カスタム skill）

## 1. 背景・動機

同一の要件を複数の長期ブランチ（develop / release-2025 / release-2024 など）に対して並行で修正することが多く、事後の作業ログ・統計時に「修正済み PR の一覧」を `分支名(#PR番号)` の形式でカンマ区切りに整形する作業が発生する。複数仓储・複数ブランチをまたぐと手動収集は煩雑であり、漏れや表記ゆれの原因になる。

`find-prs` skill は、GitHub 組織配下の全仓储を対象に PR タイトル一致で検索し、結果を一行串・tree・table のいずれかの形式で出力する。oneline 形式はクリップボードへ自動コピーし、Excel・Kintone 等へ貼り付けやすくする。

## 2. ゴール／非ゴール

### ゴール
- GitHub 組織配下の全仓储から、PR タイトルにキーワードを含む PR を一括検索する
- 結果を「一行串」「tree」「table」の 3 形式で出力できる（複数形式の併用も可）
- 一行串は仓储名・分支名に応じた可読的な表記規約を持つ
- 一行串は Windows 環境で自動的にクリップボードへコピーされる
- 既存 skill（`commit-msg` / `pr-desc` / `generate-testdoc`）と整合的なコマンド体系・配置とする

### 非ゴール
- PR の内容（diff / body）の解析
- 同名非 develop 分支が複数仓储に同時存在するケースの曖昧性解消（ユーザー確認済み：発生しない前提）
- 100 件超のページング自動継続（>100 は警告のみ）
- Windows 以外でのクリップボード対応（macOS/Linux ではスキップ）

## 3. コマンド仕様

### 構文

```
/find-prs <keyword> [--org <name>] [--state <s>] [--format <f>] [--copy|--no-copy]
```

### 引数・オプション

| 名前 | 必須 | デフォルト | 値域 | 説明 |
|------|------|-----------|------|------|
| `<keyword>` | はい | — | 任意文字列 | PR タイトル検索キーワード（例: `1234`、`患者一覧`） |
| `--org` | いいえ | `medley-inc` | 任意組織名 | GitHub 組織名 |
| `--state` | いいえ | `all` | `open` / `closed` / `merged` / `all` | PR 状態フィルタ |
| `--format` | いいえ | `oneline` | `oneline` / `tree` / `table`、カンマ区切り複数指定可 | 出力形式 |
| `--copy` / `--no-copy` | いいえ | `--copy` | フラグ | oneline をクリップボードへコピーするか（Windows のみ有効） |

### 使用例

```
/find-prs 1234
/find-prs 1234 --state merged --format tree,oneline
/find-prs 患者一覧 --format table
/find-prs 1234 --org medley-inc --format tree,table,oneline --no-copy
```

## 4. 出力形式仕様

### 4.1 oneline（デフォルト）

ルール:
- base 分支が `develop` の場合: `<repo>最新(#PR番号)`
- base 分支がそれ以外の場合: `<分支名>(#PR番号)`
- 並び順:
  1. develop 条目を先頭にまとめ、repo 名の辞書順
  2. その後、その他分支条目を分支名の辞書順
- 区切り: `, `（半角カンマ + 半角スペース）

例:

```
mall4最新(#12), mall3最新(#34), release-2024(#11), release-2025(#13)
```

### 4.2 tree

ルール:
- 行頭に repo 名（組織名なし）
- 次行から 2 スペースインデント、ツリー記号なし
- 各エントリは `<分支名>: <URL>`
- 複数 repo 間に空行を入れない（密に詰める）

例:

```
mall4
  develop: https://github.com/medley-inc/mall4/pull/12
  release-2025: https://github.com/medley-inc/mall4/pull/13
mall3
  develop: https://github.com/medley-inc/mall3/pull/34
```

### 4.3 table

Markdown 表形式。列構成:

| 列 | 内容 |
|----|------|
| 仓储:分支 | `<repo>:<分支名>`（develop の簡略化なし） |
| PR# | `#<番号>` |
| State | `open` / `closed` / `merged` |
| Title | PR タイトル原文 |
| URL | PR の HTML URL |

例:

| 仓储:分支 | PR# | State | Title | URL |
|----------|-----|-------|-------|-----|
| mall4:develop | #12 | merged | 1234 患者一覧の検索条件修正 | https://github.com/medley-inc/mall4/pull/12 |
| mall4:release-2025 | #13 | merged | 1234 患者一覧の検索条件修正 | https://github.com/medley-inc/mall4/pull/13 |

### 4.4 複数形式の併用

`--format tree,oneline` のように指定された場合、指定順に各形式を出力し、形式間は空行 1 行で区切る。

例（`--format tree,oneline`）:

```
mall4
  develop: https://...
  release-2025: https://...
mall3
  develop: https://...

mall4最新(#12), mall3最新(#34), release-2025(#13)
```

## 5. 実装方針

### 5.1 全体構成

純 Markdown skill 方式（`commit-msg` / `pr-desc` と同型）。外部スクリプトを持たず、SKILL.md 内に AI へ向けた手順を記述し、AI が `gh` CLI を呼び出して結果を整形する。

理由:
- 検索 → 集計 → 整形のロジックは単純で AI が直接遂行可能
- `gh` CLI は既プロジェクトで利用済み（generate-testdoc が依存）。新規依存ゼロ
- Python スクリプト化は過剰な間接化となる

### 5.2 実行ステップ

1. **引数パース**: keyword / org / state / format / copy を抽出。`state=all` の場合は `--state` を付けない。
2. **gh 認証チェック**: `gh auth status` が失敗する場合、`gh auth login` を促し中断。
3. **PR 検索**:

   ```
   gh search prs --owner <org> "<keyword>" --match title \
     [状態フラグ] \
     --json number,title,repository,state,url --limit 100
   ```

   状態フラグのマッピング:
   - `--state open` → `--state open`
   - `--state closed` → `--state closed`
   - `--state merged` → `--merged`（`gh search prs` の `--state` は merged を受け付けないため、別フラグを使用）
   - `--state all` → フラグ未指定（既定動作）

   `gh search prs` の JSON 出力には `baseRefName` が含まれないため、後段で別途取得が必要。
4. **base 分支補完**: 検索結果の各 PR について、

   ```
   gh pr view <number> --repo <owner/repo> --json baseRefName
   ```

   を並列実行（AI が複数 Bash ツール呼び出しを 1 メッセージ内で発行）。
5. **集計・並び替え**:
   - `repository.nameWithOwner` で groupBy
   - oneline 用: develop を先頭にまとめ → repo 辞書順、続いて非 develop を分支名辞書順
   - tree 用: repo 辞書順、各 repo 内は分支名辞書順
   - table 用: repo 辞書順、各 repo 内は分支名辞書順
6. **整形出力**: `--format` 指定順に各形式を生成、空行で区切る。
7. **クリップボード反映**:
   - `--copy` かつ Windows プラットフォームの場合のみ、`Set-Clipboard -Value "<oneline>"` を実行
   - oneline が `--format` に含まれない場合はコピー対象が存在しないため、警告して skip
   - Windows 以外は「macOS/Linux ではクリップボード未対応」と告知して skip
8. **完了報告**: ヒット件数・コピー有無を末尾に短く出力。

### 5.3 エラー・例外処理

| 状況 | 動作 |
|------|------|
| `gh auth status` 失敗 | `gh auth login` を促して中断 |
| `gh search prs` が 0 件 | 「指定キーワードに一致する PR が見つかりませんでした」と表示し正常終了 |
| 検索結果が 100 件ちょうど | 「結果が上限 100 件で切り捨てられている可能性があります。より具体的なキーワードをご検討ください」と警告 |
| `gh pr view` で 1 件だけ失敗 | 当該 PR をスキップし、警告ログを残して継続 |
| `--copy` 指定だが oneline が含まれない | コピー対象がないため skip + 警告 |
| Windows 以外で `--copy` | クリップボード未対応として skip + 告知 |

## 6. ファイル構成

```
tools/find-prs/
├── SKILL.md      # 主指示書（frontmatter + 仕様 + 実行手順）
└── examples.md   # 入出力サンプル
```

`README.md` の `tools` 表に 1 行追加:

```
| [find-prs](tools/find-prs/SKILL.md) | `/find-prs <keyword> [opts]` | 組織横断で PR を検索し、一行串/tree/table で出力 |
```

### 6.1 SKILL.md 骨格

1. YAML frontmatter（`name: find-prs`、`description: ...`、`when to use: ...`）
2. コマンド構文（§3）
3. 引数仕様表（§3）
4. 前提チェック（gh 認証・プラットフォーム判定）
5. 実行ステップ（§5.2）
6. 出力形式仕様（§4）
7. エラー・例外処理（§5.3）
8. 参考用 `gh` コマンド例

### 6.2 examples.md 骨格

- 例 1: `/find-prs 1234` → oneline + 自動コピー
- 例 2: `/find-prs 1234 --format tree,oneline --state merged`
- 例 3: `/find-prs 患者一覧 --format table`
- 例 4: 0 件結果
- 例 5: 100 件上限警告

## 7. オープン事項

なし（ブレインストーミング段階で全項目を確定済み）。

## 8. 参考

- 既存スキル: [commit-msg](../../../git/commit-msg/SKILL.md), [pr-desc](../../../git/pr-desc/SKILL.md), [generate-testdoc](../../../tools/generate-testdoc/SKILL.md)
- GitHub CLI `gh search prs` ドキュメント: https://cli.github.com/manual/gh_search_prs
- GitHub CLI `gh pr view` ドキュメント: https://cli.github.com/manual/gh_pr_view
