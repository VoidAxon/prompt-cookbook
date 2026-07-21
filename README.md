# prompt-cookbook

Claude Code 用のカスタムスキル（スラッシュコマンド）とプロンプト集。

## セットアップ

### グローバル（全プロジェクトで使用）

`~/.claude/skills/` 以下に置くだけで自動的に全プロジェクトで有効になります。

```bash
git clone https://github.com/voidaxon/prompt-cookbook.git ~/.claude/skills/prompt-cookbook
```

### プロジェクト単位（特定プロジェクトでのみ使用）

**git submodule として追加する場合**

```bash
cd your-project
git submodule add https://github.com/voidaxon/prompt-cookbook.git .claude/skills/prompt-cookbook
```

**特定スキルだけ使いたい場合はシンボリックリンク**

```bash
# グローバルにクローン済みの前提
ln -s ~/.claude/skills/prompt-cookbook/git/commit-msg .claude/skills/commit-msg
ln -s ~/.claude/skills/prompt-cookbook/git/pr-desc    .claude/skills/pr-desc
```

## スキル一覧

### git

| スキル | コマンド | 概要 |
|--------|----------|------|
| [commit-msg](git/commit-msg/SKILL.md) | `/commit-msg <mode> [context]` | 規約に沿った日本語コミットメッセージを生成 |
| [pr-desc](git/pr-desc/SKILL.md) | `/pr-desc <mode> [context]` | レビュアー向けの日本語 PR 説明文を生成 |

### tools

| スキル | コマンド | 概要 |
|--------|----------|------|
| [snap](tools/snap/SKILL.md) | `/snap [prompt]` | クリップボードの画像を Claude CLI から直接分析 |
| [snappath](tools/snappath/SKILL.md) | `/snappath` | クリップボードの画像を一時ファイルに保存しパスを返す |
| [generate-testdoc](tools/generate-testdoc/SKILL.md) | `/generate-testdoc pr <no>` | PRまたはコミットの差分からテスト仕様書（Excel）を生成 |
| [find-prs](tools/find-prs/SKILL.md) | `/find-prs <keyword> [opts]` | 組織横断で PR タイトル検索し、oneline/tree/table で出力 |
| [spec-impl-reconcile](tools/spec-impl-reconcile/SKILL.md) | `/spec-impl-reconcile <仕様書パス> <クラス名> [md/excel/both]` | 設計書と実装を突合し記載漏れ・相違・要確認を課題リスト（Excel）化 |

## 使い方

各スキルは `<mode>` と任意の `[context]` を引数に取ります。

### mode

| 値 | 説明 |
|----|------|
| `stage` | ステージングされた差分から生成 |
| `latest` | 直近のコミット履歴から生成 |
| `commit <id>` | 指定したコミット ID から生成 |

### context（任意）

チケット番号・背景・注意点など、差分だけでは伝わらない補足情報を渡せます。

```
/commit-msg stage ABC-123 ログイン画面のバリデーション追加
/pr-desc latest
/pr-desc commit a1b2c3d
```

サンプル出力は各スキルの `examples.md` を参照してください。

---

## generate-testdoc

PRまたはコミットの差分を解析し、**変更された箇所のみ**を対象としたテスト観点・テストケースを Excel テンプレートへ出力するスキル。

### 必要な環境

| 依存 | 用途 |
|------|------|
| **Python 3.8 以上** | Excel 生成スクリプトの実行 |
| **openpyxl** | Excel ファイルの読み書き |
| **gh CLI** | `--pr` 指定時の PR 差分・説明文取得 |

```bash
# Python パッケージのインストール
pip install openpyxl

# gh CLI の認証（--pr を使う場合）
gh auth login
```

### セットアップ

```bash
# スキルディレクトリにコピー
cp -r tools/generate-testdoc ~/.claude/skills/generate-testdoc
```

### 使い方

**`--pr` を使う場合（最も一般的）**

PR タイトルが `1234 患者一覧の検索条件修正` のように `KintoneID タイトル` の形式であれば、PR 番号だけで実行できます。KintoneID とタイトルは PR タイトルから自動的に抽出されます。

```
/generate-testdoc pr 456
/generate-testdoc pr 456 repo medley-inc/mall3   # 別リポジトリ
```

**KintoneID・タイトルを手動指定する場合**

`commit` やステージング差分を使う場合は明示的に指定します。

```
/generate-testdoc 1234 患者一覧の検索条件修正 commit abc1234
/generate-testdoc 1234 患者一覧の検索条件修正
```

### 出力

Excel ファイルが `~/Documents/docs/testcase/【{KintoneID}】 {Title}.xlsx` に生成されます。

| シート | 内容 |
|--------|------|
| テスト観点シート | B列: No.、C列: テスト観点グループ名、D列: 確認項目（箇条書き） |
| テストケースシート | A列: 項番、B列: テスト名、C列: 前提条件、D列: 操作手順、E列: 期待値 |

### テスト観点の設計方針

差分の変更種別・リスク度に応じて以下の7角度をテスト設計の思考チェックリストとして活用する。7角度は AI がテストケースを漏れなく生成するための思考軸であり、シートには機能エリア単位のグループ名と確認項目が出力される。

| # | テスト観点 | 主な用途 |
|---|-----------|---------|
| ① | 正常系 | 通常フロー・設定通りの初期表示 |
| ② | 異常系・堅牢性 | null・空文字・型不一致・例外スロー確認 |
| ③ | 境界値・極限 | 最大/最小値・境界±1・日付の年跨ぎ・うるう年 |
| ④ | 権限・セキュリティ | 権限あり/なし・越権アクセス |
| ⑤ | 操作性・UX | リアルタイムフィードバック・即時反映 |
| ⑥ | 連携・複合条件 | 他機能との組み合わせ・相互影響 |
| ⑦ | 回帰確認 | 既存機能への変更影響なし（常に追加） |

---

## find-prs

GitHub 組織配下の全リポジトリから PR タイトルを検索し、結果を **oneline / tree / table** の 3 形式で整形出力するスキル。同じ要件の修正が複数の長期ブランチに分散している状況で、横断的に確認・コピペするのに使う。

### 必要な環境

| 依存 | 用途 |
|------|------|
| **gh CLI** | PR 検索と base 分支取得 |
| **PowerShell**（Windows のみ） | `--copy` 明示時に oneline 結果をクリップボードへコピー |

```bash
gh auth login
```

### 使い方

```
/find-prs <keyword> [--org <name>] [--state <s>] [--format <f>] [--copy|--no-copy]
```

| オプション | 既定 | 値域 | 説明 |
|-----------|------|------|------|
| `<keyword>` | — | 任意文字列 | PR タイトル検索キーワード（例: `1234`、`患者一覧`） |
| `--org` | `medley-inc` | 任意組織名 | GitHub 組織名 |
| `--state` | `all` | `open` / `closed` / `merged` / `all` | PR 状態フィルタ |
| `--format` | `table` | `oneline` / `tree` / `table`（カンマ区切り併用可） | 出力形式 |
| `--copy` / `--no-copy` | `--no-copy` | フラグ | `--copy` 明示指定時のみ Windows でクリップボードへコピー（既定はコピーしない） |

```
/find-prs 1234                                          # 既定: table 形式、コピーなし
/find-prs 1234 --state merged --format tree,oneline     # merged のみ・tree と oneline 併用
/find-prs 1234 --format oneline --copy                  # oneline をクリップボードへコピー
```

### 出力形式

| 形式 | 用途 |
|------|------|
| `oneline` | Excel / Kintone 等に貼り付ける 1 行サマリ（例: `mall4最新(#12), release-2025(#13), mall3最新(#34)`） |
| `tree` | repo / 分支 / URL をプレフィックス・インデント無しのフラット行リストで表示（repo 名は単独行、分支行は `分支名: URL` で識別） |
| `table` | ブランチ・PR#・State・URL の表形式。タイトルが共通プレフィックスで 1 つに集約できる場合は Title 列を除いて表上に 1 行表示、複数の異なるタイトルが残る場合は Title 列に表示 |

いずれの形式でも repo グループ単位で連続出力されます。**medley-inc 既定の repo 優先順位は `mall4` → `mall3` → `mall-jinei` → その他（辞書順）**。各 repo 内では `develop` を先頭にし、他分支は分支名の辞書順で並びます。

table の Title 扱いは、共通プレフィックス集約後の残り件数で切り替わります：
- **1 件**（例: `163092 ...` と `163092 ... m3-202508` のように末尾だけ違う）→ Title 列を削除し、表上に `**Title:** ...` を 1 行表示
- **2 件以上**（明らかに異なるタイトル群）→ Title 列を表内に保持

詳細仕様は [tools/find-prs/SKILL.md](tools/find-prs/SKILL.md)、出力サンプルは [tools/find-prs/examples.md](tools/find-prs/examples.md) を参照してください。

---

## spec-impl-reconcile

設計書（機能仕様書・詳細設計書）と実装コードを突合し、**記載漏れ・相違・要確認**を洗い出して課題リスト化するスキル。実装を唯一の事実とし、AI生成仕様書のハルシネーション（実在しない Service/Repository 等）や欠落を検出する。**バグ探しではなく要件整理が主眼。read-only（設計書・実装を編集しない）。領域・言語非依存**。

### 必要な環境

| 依存 | 用途 |
|------|------|
| **Python 3.8 以上** | ③転記表の Excel 化・機械チェック（`scripts/pipe_to_xlsx.py`） |
| **openpyxl** | `.xlsx` 生成（無ければ UTF-8 BOM 付き CSV へ自動降級） |

```bash
pip install openpyxl
```

### 使い方

```
/spec-impl-reconcile <仕様書パス> <クラス名/画面名> [md|excel|both]
```

実在ゲート（仕様書が挙げる核心シンボルの実在確認）→ 機械枚举母集団突合＋分節並行検証 → 完整性クリティック＋アドバサリアル収束ゲート → 出力（**①結論 / ②1指摘=1ブロック / ③転記用 / ④人による最終確認**）。`format` は `md`（レポート .md・既定）/ `excel`（真 xlsx）/ `both`。

### 出力

既定で `%USERPROFILE%\Documents\<対象名>\<対象名>_issues.xlsx` に生成（既存ファイルは同フォルダの `old\` へ退避）。③転記表を単独で Excel 化する場合:

```
python tools/spec-impl-reconcile/scripts/pipe_to_xlsx.py <③を書き出したファイル> --name <対象名>
```

課題リストの列: `課題ID / 対象 / 指摘箇所 / 指摘内容 / 分類（A1〜E）/ 深刻度（高中低）/ 確度（Confirmed・Inferred・Gap）/ 対処区分 / 備考`。詳細は [tools/spec-impl-reconcile/SKILL.md](tools/spec-impl-reconcile/SKILL.md) と `references/` を参照。

---

## ディレクトリ構成

```
prompt-cookbook/
├── git/
│   ├── commit-msg/
│   │   ├── SKILL.md
│   │   └── examples.md
│   └── pr-desc/
│       ├── SKILL.md
│       └── examples.md
└── tools/
    ├── snap/
    │   ├── SKILL.md
    │   └── snap.ps1              # スタンドアロン利用時の PowerShell スクリプト
    ├── snappath/
    │   └── SKILL.md
    ├── find-prs/
    │   ├── SKILL.md
    │   └── examples.md
    ├── generate-testdoc/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   └── generate_testdoc.py   # Excel 生成スクリプト（要 Python + openpyxl）
    │   └── templates/
    │       └── test_spec_template.xlsx
    └── spec-impl-reconcile/
        ├── SKILL.md
        ├── references/
        │   ├── review-method.md      # 実在ゲート・3レンズ・機械枚举母集団突合・収束ゲート
        │   ├── output-format.md      # ①〜④・指摘箇所許可値・format・機械チェック
        │   └── subagent-prompt.md    # 分節サブエージェント雛形
        └── scripts/
            └── pipe_to_xlsx.py       # ③転記表→機械チェック→真 xlsx（要 Python + openpyxl）
```
