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
