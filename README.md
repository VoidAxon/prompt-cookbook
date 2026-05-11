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

## ディレクトリ構成

```
prompt-cookbook/
└── git/
    ├── commit-msg/
    │   ├── SKILL.md
    │   └── examples.md
    └── pr-desc/
        ├── SKILL.md
        └── examples.md
```
