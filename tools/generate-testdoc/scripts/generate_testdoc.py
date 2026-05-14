#!/usr/bin/env python3
"""Generate test specification Excel document from JSON input."""

import argparse
import glob
import json
import re
import sys
import zipfile
from pathlib import Path

try:
    import openpyxl
    from openpyxl.styles import Alignment
except ImportError:
    print("[ERROR] openpyxl が必要です。pip install openpyxl でインストールしてください。")
    sys.exit(1)

SKILL_ROOT = Path(__file__).parent.parent
TEMPLATE_PATH = SKILL_ROOT / "templates" / "test_spec_template.xlsx"


def load_json(input_path=None):
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def resolve_output_path(output_dir, kintone_id, title):
    output_dir = Path(output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = glob.glob(str(output_dir / f"【{kintone_id}】*.xlsx"))
    if len(existing) > 1:
        print(f"[WARNING] 同一KintoneIDのファイルが複数存在します。最初のファイルを更新します: {existing[0]}")
    if existing:
        return Path(existing[0])
    return output_dir / f"【{kintone_id}】 {title}.xlsx"


def load_workbook(output_path):
    if output_path.exists():
        return openpyxl.load_workbook(output_path)
    if TEMPLATE_PATH.exists():
        return openpyxl.load_workbook(TEMPLATE_PATH)
    print(f"[ERROR] テンプレートが見つかりません: {TEMPLATE_PATH}")
    sys.exit(1)


def find_sheet(wb, keywords):
    for name in wb.sheetnames:
        if any(kw in name for kw in keywords):
            return wb[name]
    return None


def set_row_height(ws, row, columns):
    """改行数に基づいて行の高さを設定する。"""
    max_lines = 1
    for col in columns:
        value = ws.cell(row=row, column=col).value
        if value:
            max_lines = max(max_lines, str(value).count("\n") + 1)
    ws.row_dimensions[row].height = max_lines * LINE_HEIGHT


def set_text_cell(ws, row, col, value):
    """値をテキスト形式で書き込む。number_format="@" により Excel が数式と誤認識しない。"""
    cell = ws.cell(row=row, column=col, value=value)
    cell.number_format = "@"
    cell.alignment = Alignment(wrap_text=True, vertical="top")


def write_test_viewpoints(ws, viewpoints):
    start_row = 6  # row 5 = header, row 6 = data start
    for i, vp in enumerate(viewpoints):
        row = start_row + i
        set_text_cell(ws, row, 3, vp["category"])
        set_text_cell(ws, row, 4, vp["item"])


def write_test_cases(ws, test_cases):
    start_row = 9
    for i, tc in enumerate(test_cases):
        row = start_row + i
        steps_text = "\n".join(f"{j + 1}. {step}" for j, step in enumerate(tc["steps"]))
        set_text_cell(ws, row, 2, tc["viewpoint"])
        set_text_cell(ws, row, 3, tc["precondition"])
        set_text_cell(ws, row, 4, steps_text)
        set_text_cell(ws, row, 5, tc["expected"])


def fix_inline_strings(xlsx_path):
    """openpyxlが生成する inlineStr セルを shared strings に変換して Excel の #NAME? を回避する。"""
    xlsx_path = Path(xlsx_path)

    with zipfile.ZipFile(xlsx_path, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    sheet_names = [n for n in files if n.startswith("xl/worksheets/") and n.endswith(".xml")]

    def _decode_xml(text):
        """&#NNNN; などの XML 文字参照を Unicode 文字に戻す。"""
        text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
        text = re.sub(r"&#x([0-9a-fA-F]+);", lambda m: chr(int(m.group(1), 16)), text)
        return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')

    def _escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # inlineStr の生テキスト（XML エンティティ含む）→ shared strings インデックス
    encoded_to_idx = {}
    decoded_list = []

    for name in sheet_names:
        for encoded in re.findall(
            r't="inlineStr"[^>]*><is><t[^>]*>(.*?)</t></is></c>',
            files[name].decode("utf-8"),
            re.DOTALL,
        ):
            if encoded not in encoded_to_idx:
                encoded_to_idx[encoded] = len(decoded_list)
                decoded_list.append(_decode_xml(encoded))

    if not decoded_list:
        return

    # 各シートの inlineStr セルを t="s" に置換し、行高さをExcelに委ねる
    for name in sheet_names:
        xml = files[name].decode("utf-8")

        def _replace(m):
            attrs = re.sub(r'\s*t="inlineStr"', "", m.group(1))
            idx = encoded_to_idx.get(m.group(2))
            return f'<c{attrs} t="s"><v>{idx}</v></c>' if idx is not None else m.group(0)

        xml = re.sub(
            r'<c([^>]+)t="inlineStr"[^>]*><is><t[^>]*>(.*?)</t></is></c>',
            _replace,
            xml,
            flags=re.DOTALL,
        )
        # ht / customHeight を除去 → Excel がファイルを開いた際に自動で行高さを計算する
        xml = re.sub(r'\s+ht="[^"]*"', "", xml)
        xml = re.sub(r'\s+customHeight="[^"]*"', "", xml)
        files[name] = xml.encode("utf-8")

    # sharedStrings.xml を生成（改行・先頭末尾空白がある場合は xml:space="preserve"）
    count = len(decoded_list)
    ss_items = []
    for text in decoded_list:
        escaped = _escape_xml(text)
        preserve = ' xml:space="preserve"' if ("\n" in text or text != text.strip()) else ""
        ss_items.append(f"<si><t{preserve}>{escaped}</t></si>")

    files["xl/sharedStrings.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        f' count="{count}" uniqueCount="{count}">'
        + "".join(ss_items)
        + "</sst>"
    ).encode("utf-8")

    # [Content_Types].xml に sharedStrings エントリを追加
    ct = files["[Content_Types].xml"].decode("utf-8")
    if "sharedStrings" not in ct:
        ct = ct.replace(
            "</Types>",
            '<Override PartName="/xl/sharedStrings.xml"'
            ' ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
            "</Types>",
        )
        files["[Content_Types].xml"] = ct.encode("utf-8")

    # workbook.xml.rels に sharedStrings リレーションを追加
    rels_name = "xl/_rels/workbook.xml.rels"
    if rels_name in files:
        rels = files[rels_name].decode("utf-8")
        if "sharedStrings" not in rels:
            rids = re.findall(r'Id="rId(\d+)"', rels)
            next_id = max(int(r) for r in rids) + 1 if rids else 10
            rels = rels.replace(
                "</Relationships>",
                f'<Relationship Id="rId{next_id}"'
                f' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings"'
                f' Target="sharedStrings.xml"/></Relationships>',
            )
            files[rels_name] = rels.encode("utf-8")

    # 上書き保存
    tmp = xlsx_path.with_suffix(".tmp.xlsx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in files.items():
            zout.writestr(name, data)
    xlsx_path.unlink()
    tmp.rename(xlsx_path)


def main():
    parser = argparse.ArgumentParser(description="テスト仕様書Excelを生成する")
    parser.add_argument("--kintone-id", required=True, help="KintoneチケットID")
    parser.add_argument("--title", required=True, help="変更タイトル")
    parser.add_argument("--input", help="JSONファイルパス（省略時はstdin）")
    parser.add_argument("--output", default="~/Documents/docs/testcase/", help="出力ディレクトリ")
    args = parser.parse_args()

    try:
        data = load_json(args.input)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[ERROR] JSON読み込みに失敗しました: {e}")
        sys.exit(1)

    output_path = resolve_output_path(args.output, args.kintone_id, args.title)
    wb = load_workbook(output_path)

    sheet_viewpoints = find_sheet(wb, ["観点"])
    sheet_cases = find_sheet(wb, ["ケース"])

    if sheet_viewpoints is None or sheet_cases is None:
        print(f"[ERROR] テンプレートに 'テスト観点' または 'テストケース' シートが見つかりません。")
        print(f"  シート一覧: {wb.sheetnames}")
        sys.exit(1)

    write_test_viewpoints(sheet_viewpoints, data["test_viewpoints"])
    write_test_cases(sheet_cases, data["test_cases"])

    wb.save(output_path)
    fix_inline_strings(output_path)

    print(f"[完了] テスト仕様書を出力しました。")
    print(f"  ファイル: {output_path}")
    print(f"  テスト観点: {len(data['test_viewpoints'])} 件")
    print(f"  テストケース: {len(data['test_cases'])} 件")


if __name__ == "__main__":
    main()
