#!/usr/bin/env python3
"""③転記用（パイプ区切り）テーブルを検査し、xlsx（無ければCSVへ降級）に変換する。

spec-impl-reconcile の出力 ③ を人手変換せずに Excel で開ける成果物へ落とすための再利用ツール。
- 入力: パイプ `|` 区切りのテキスト（1行目ヘッダ、以降1指摘=1行）。ファイル or stdin。
- 検査（機械チェック）: 全行のパイプ本数が揃うか / 先頭・末尾パイプが無いか / 非日本語スクリプト混入。
- 出力: <out>.xlsx（openpyxl があれば）。無ければ <out>.csv（UTF-8 BOM・必要時クォート）へ降級し警告。

使い方:
    python pipe_to_xlsx.py <input_pipe.txt> <output_base>   # 明示: out\\Foo_issues （拡張子は付けない）
    python pipe_to_xlsx.py <input_pipe.txt> --name <対象名>  # 既定: %USERPROFILE%\\Documents\\<対象名>\\<対象名>_issues
    cat table.txt | python pipe_to_xlsx.py - --name <対象名>

出力先:
- <output_base> を明示した場合はそこへ書く。
- 省略し --name <対象名> を渡した場合、既定の %USERPROFILE%\\Documents\\<対象名>\\<対象名>_issues に書く（フォルダは自動作成）。
- 既存の同名ファイルは同フォルダの old\\ へ退避してから上書きする（黙って消さない）。

終了コード: 0=成功, 1=引数不足, 2=構造エラー（パイプ本数不一致・首尾パイプ）, 3=生成失敗。
非日本語スクリプト混入は警告のみ（μ 等の正当な記号もあるため、人が最終確認する前提）。
"""
import os
import sys
import re
import csv

# キリル/ギリシャ/ヘブライ/アラビア/タイ/ハングル等（生成タイポの検出用。日本語=かな/漢字は対象外）
FORBIDDEN = re.compile(r"[Ͱ-ϿЀ-ӿ֐-׿؀-ۿ฀-๿가-힯]")


def parse(text):
    """パイプ区切りテキストを行×セルの2次元リストへ。各セルはトリムする。"""
    rows = []
    for line in text.splitlines():
        if line.strip() == "":
            continue
        # 先頭・末尾パイプは構造エラーとして後段で検出するため、ここでは strip しない
        rows.append([c.strip() for c in line.split("|")])
    return rows


def check(rows, raw_lines, sections=None):
    """機械チェック。致命的エラーのリストと警告のリストを返す。

    sections: 指摘箇所の許可値リスト（渡された時のみ列3を照合・一覧外は警告）。
    """
    errors, warnings = [], []
    if not rows:
        return ["入力が空です"], warnings
    ncol = len(rows[0])
    # 指摘箇所は既定で3列目（0始まりで index 2）。ヘッダ名からも探す。
    sec_idx = 2
    for j, h in enumerate(rows[0]):
        if h.strip() == "指摘箇所":
            sec_idx = j
            break
    for i, (cells, raw) in enumerate(zip(rows, raw_lines), 1):
        if len(cells) != ncol:
            errors.append(f"{i}行目: 列数 {len(cells)}（ヘッダは {ncol}）— パイプ本数不一致")
        if raw.startswith("|") or raw.rstrip().endswith("|"):
            errors.append(f"{i}行目: 先頭または末尾にパイプがあります")
        m = FORBIDDEN.search(raw)
        if m:
            warnings.append(f"{i}行目: 非日本語スクリプト文字 {m.group()!r} を検出（生成タイポの可能性・要確認）")
        if sections and i > 1 and sec_idx < len(cells):
            v = cells[sec_idx].strip()
            if v not in sections:
                warnings.append(f"{i}行目: 指摘箇所 {v!r} が許可値一覧に無い（かっこ書き残り/§付き/複数併記/寄せ漏れを確認）")
    return errors, warnings


def write_xlsx(rows, path):
    """openpyxl で xlsx を書く。ヘッダ太字・オートフィルタ・折返し・列幅調整。失敗時は例外。"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "issues"
    for r in rows:
        ws.append(r)
    for c in range(1, len(rows[0]) + 1):
        ws.cell(row=1, column=c).font = Font(bold=True)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(rows[0]))}{len(rows)}"
    # 列幅: 見出し名で判定。長文列（指摘内容/備考）は広め＋折返し
    wide = {"指摘内容", "備考"}
    for idx, name in enumerate(rows[0], 1):
        col = get_column_letter(idx)
        ws.column_dimensions[col].width = 80 if name in wide else min(max(len(name) + 4, 10), 24)
        if name in wide:
            for row in range(2, len(rows) + 1):
                ws.cell(row=row, column=idx).alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(path)


def write_csv(rows, path):
    """UTF-8 BOM・必要時クォートの CSV（Excel が直接開ける降級版）。"""
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerows(rows)


def parse_opts(argv):
    """argv[2:] を解析して (out_base, sections) を返す。

    --name <対象名>   → 既定 %USERPROFILE%\\Documents\\<対象名>\\<対象名>_issues（フォルダ作成）
    --sections a,b,c  → 指摘箇所の許可値（カンマ区切り。値トークンを消費）
    それ以外の位置引数 → 明示 output_base
    """
    args = argv[2:]
    name = None
    sections = None
    positional = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--name" and i + 1 < len(args):
            name = args[i + 1]; i += 2; continue
        if a == "--sections" and i + 1 < len(args):
            sections = [s.strip() for s in args[i + 1].split(",") if s.strip()]; i += 2; continue
        if not a.startswith("--"):
            positional = a
        i += 1

    if positional:
        out_base = positional
    elif name:
        home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
        d = os.path.join(home, "Documents", name)
        os.makedirs(d, exist_ok=True)
        out_base = os.path.join(d, name + "_issues")
    else:
        out_base = None
    return out_base, sections


def stash_old(path):
    """既存の同名ファイルを同フォルダの old\\ へ退避（衝突時は連番）。黙って上書きしない。"""
    if not os.path.exists(path):
        return
    d = os.path.dirname(path) or "."
    base = os.path.basename(path)
    oldd = os.path.join(d, "old")
    os.makedirs(oldd, exist_ok=True)
    dest = os.path.join(oldd, base)
    root, ext = os.path.splitext(base)
    n = 1
    while os.path.exists(dest):
        dest = os.path.join(oldd, f"{root}_{n}{ext}")
        n += 1
    os.replace(path, dest)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    src = argv[1]
    out_base, sections = parse_opts(argv)
    if not out_base:
        print("[ERROR] 出力先が未指定です。<output_base> か --name <対象名> を渡してください。", file=sys.stderr)
        print(__doc__)
        return 1
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    raw_lines = [l for l in text.splitlines() if l.strip() != ""]
    rows = parse(text)

    errors, warnings = check(rows, raw_lines, sections)
    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        print("[NG] 機械チェックに失敗。③を修正してから再実行してください。", file=sys.stderr)
        return 2

    try:
        path = out_base + ".xlsx"
        stash_old(path)
        write_xlsx(rows, path)
        print(f"[OK] xlsx を生成: {path}")
        return 0
    except ImportError:
        path = out_base + ".csv"
        stash_old(path)
        write_csv(rows, path)
        print(f"[WARN] openpyxl が無いため xlsx を生成できず CSV へ降級: {path}", file=sys.stderr)
        print("       真の xlsx が必要なら: pip install openpyxl（または PowerShell の ImportExcel）", file=sys.stderr)
        return 0
    except Exception as e:  # 生成失敗も CSV へ降級して成果物は必ず残す
        path = out_base + ".csv"
        try:
            stash_old(path)
        except Exception:
            pass
        write_csv(rows, path)
        print(f"[WARN] xlsx 生成に失敗（{e}）。CSV へ降級: {path}", file=sys.stderr)
        if isinstance(e, PermissionError) or "WinError 32" in str(e):
            print("       → 出力先 xlsx が使用中（Excel で開いていないか）。閉じてから再実行してください。", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
