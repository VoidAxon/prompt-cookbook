# スクリプト実行と出力（generate-testdoc Step 6）

generate-testdoc の SKILL.md「Step 6」から参照される、Excel 生成スクリプトの実行手順。JSON スキーマは SKILL.md の 6.1 にある。

## スクリプト実行

JSON を一時ファイルに保存してスクリプトを呼び出す。

**注意：** Windows では Bash `/tmp/` と Python `tempfile.gettempdir()` が異なる場合がある。Python の一時ディレクトリ（例: `C:/Users/<user>/AppData/Local/Temp/`）に直接保存すること。

```bash
# プロジェクト優先でスキルディレクトリ特定
SKILL_DIR=".claude/skills/generate-testdoc"
[ ! -d "$SKILL_DIR" ] && SKILL_DIR="$HOME/.claude/skills/generate-testdoc"

python "$SKILL_DIR/scripts/generate_testdoc.py" \
  --kintone-id "<KintoneID>" \
  --title "<Title>" \
  --input "<TempDir>/testdoc_<KintoneID>.json"
```

→ `【KintoneID】 <Title>.xlsx` で出力される。

**同名ファイルがある場合は上書きしない（バージョン採番）：** 出力先に同名ファイルが既に存在する場合、既存ファイルを上書き・更新せず、ファイル名末尾にバージョン番号を付けた**新規ファイル**を作成する。`【ID】 <Title>.xlsx` が既存なら `【ID】 <Title>_v2.xlsx`、それも既存なら `_v3` …と、存在しない名前になるまで番号を上げる。生成は毎回テンプレートから行うため、前回生成データの残留は発生しない。

## PR 由来の場合のヘッダー書き込み（C3/C4）

入力が `pr <number>` の場合、上記コマンドに以下を**必ず追加**する。テスト観点シートのヘッダーに PR 情報が書き込まれる：

```bash
  --pr-no "<PR番号>" \
  --pr-url "https://github.com/<owner>/<repo>/pull/<PR番号>" \
  --pr-title "<PRタイトル（KintoneID除去済み）>" \
  --record-url "<PR本文から抽出したcybozuリンク>"   # 見つからなければ省略
```

| セル | 内容 |
|------|------|
| C3（kintoneレコード） | `--pr-title` の文字列。`--record-url` 指定時はそのリンク付き、なければ文字のみ |
| C4（シェルブセット） | `#<PR番号>`（例: `#1234`）。`--pr-url` のリンク付き |

- `--pr-title` は PR タイトルから先頭の KintoneID トークンを除去した残り（Step 1 で抽出した Title と同じ。ファイル分割時の識別情報サフィックスは付けない）
- `--record-url` は PR 本文（body）中の URL のうち `cybozu` を含む最初のもの。なければ省略する（C3 は文字のみになる）
- commit / staged 由来の場合はこれらの引数を付けない（C3/C4 は書き込まれない）

## ファイル分割（変更量が多いケース）

以下に該当する場合、JSON とタイトルを分けて複数ファイル出力：

- 変更が独立した機能エリアにまたがり、担当者が別々に実施
- 1 ファイルに 20 件大幅超のケースが集中
- インフラ変更と業務ロジック変更が混在

`--title` 末尾に識別情報（`（新機能）`・`（既存改修）`・`（算定管理）`・`（印刷）`・`（DB移行）` 等、変更内容に合わせる）を付け、`--input` を分けてファイルごとに実行する：

```bash
python "$SKILL_DIR/scripts/generate_testdoc.py" \
  --kintone-id "<KintoneID>" --title "<Title>（新機能）" \
  --input "<TempDir>/testdoc_<KintoneID>_1.json"
```

→ `【KintoneID】 <Title>（新機能）.xlsx` のように、識別情報付きで出力される。
