#!/usr/bin/env python3
"""詳細設計書 md → 単一ファイル HTML 変換。
usage: python3 build_html.py <input.md> [output.html]
md が正本。HTML は閲覧用ビュー（編集しない）。"""
import sys, re, html
from pathlib import Path
import markdown

CSS = """
:root{--ink:#1f2430;--sub:#5a6372;--line:#dde2ea;--bg:#f6f7f9;--card:#fff;
--accent:#2f6fed;--warn-bg:#fff6e5;--warn-bd:#e6a23c;--th:#eef1f6;}
*{box-sizing:border-box}
body{margin:0;font-family:"Yu Gothic UI","Hiragino Sans","Noto Sans JP",Meiryo,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.75;font-size:15px}
.layout{display:flex;max-width:1280px;margin:0 auto}
nav{width:290px;flex:none;position:sticky;top:0;height:100vh;overflow-y:auto;
padding:24px 16px;border-right:1px solid var(--line);background:var(--card);font-size:13px}
nav a{display:block;color:var(--sub);text-decoration:none;padding:3px 8px;border-radius:4px}
nav a:hover{background:var(--bg);color:var(--accent)}
nav .l2{font-weight:600;color:var(--ink);margin-top:8px}
nav .l3{padding-left:20px}
main{flex:1;min-width:0;padding:36px 48px;background:var(--card)}
h1{font-size:26px;border-bottom:3px solid var(--accent);padding-bottom:10px}
h2{font-size:20px;margin-top:44px;padding:6px 12px;border-left:5px solid var(--accent);
background:linear-gradient(90deg,#eef3fe,transparent)}
h3{font-size:16px;margin-top:28px;color:var(--accent)}
h4{font-size:15px;margin-top:22px;padding-left:8px;border-left:3px solid var(--sub)}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.5px;background:#fff}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}
th{background:var(--th);font-weight:600;white-space:nowrap}
tr:nth-child(even) td{background:#fafbfd}
code{background:#f1f3f7;border-radius:4px;padding:1px 5px;
font-family:Consolas,"Cascadia Code",monospace;font-size:.9em}
pre{background:#282c34;color:#e6e6e6;padding:14px 18px;border-radius:8px;
overflow-x:auto;font-size:13px;line-height:1.55}
pre code{background:none;color:inherit;padding:0}
.mermaid{background:#fff;border:1px solid var(--line);border-radius:8px;
padding:12px;margin:12px 0;text-align:center}
.unconfirmed{background:var(--warn-bg);border:1px solid var(--warn-bd);
border-radius:4px;padding:0 6px;font-weight:600;color:#8a5a00}
blockquote{margin:0;padding:8px 16px;border-left:4px solid var(--warn-bd);
background:var(--warn-bg);border-radius:0 6px 6px 0}
@media print{nav{display:none}main{padding:0}}
"""

_LIST_RE = re.compile(r"^\s*(\d+\.|[-*])\s+")

def _ensure_blank_before_lists(text: str) -> str:
    """Markdown はリスト開始行の直前に空行が無いと段落に連結され、
    番号/箇条書きが1行に潰れる。リストの先頭項目の前に空行を補う
    （純粋な描画上の正規化。本文の意味は変えない）。コードフェンス内は対象外。"""
    out, in_code = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and _LIST_RE.match(line):
            prev = out[-1] if out else ""
            # 直前が空行でも既存のリスト項目でもない＝リスト開始とみなし空行を挿入
            if prev.strip() != "" and not _LIST_RE.match(prev):
                out.append("")
        out.append(line)
    return "\n".join(out)

def build(src: Path, dst: Path):
    text = src.read_text(encoding="utf-8")
    # HTML コメント（テンプレのガイド）は残す/消す → ビューでは消す
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # リスト開始前に空行を補い、番号/箇条書きが1行に潰れるのを防ぐ
    text = _ensure_blank_before_lists(text)
    # mermaid ブロックを div へ退避
    stash = []
    def _mer(m):
        stash.append(m.group(1)); return f"\n@@MERMAID{len(stash)-1}@@\n"
    text = re.sub(r"```mermaid\n(.*?)```", _mer, text, flags=re.S)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"],
                           extension_configs={"toc": {"slugify": lambda v,s: re.sub(r"[^\w\-一-龠ぁ-ゖァ-ヺ]+","-",v)}})
    body = md.convert(text)
    for i, code in enumerate(stash):
        body = body.replace(f"@@MERMAID{i}@@",
                            f'<div class="mermaid">{html.escape(code)}</div>')
        body = body.replace(f"<p>@@MERMAID{i}@@</p>",
                            f'<div class="mermaid">{html.escape(code)}</div>')
    # 未確認の強調
    body = re.sub(r"(?<![\w>])未確認(?![\w<])", '<span class="unconfirmed">未確認</span>', body)
    title = re.search(r"^# (.+)$", text, re.M)
    title = title.group(1) if title else src.stem
    dst.write_text(f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>{html.escape(title)}</title><style>{CSS}</style>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({{startOnLoad:true,theme:"neutral"}});</script>
</head><body><div class="layout">
<nav>{re.sub(r'<li><a href="(#[^"]+)">([^<]+)</a>(<ul>)?',
             lambda m: f'<a class="l2" href="{m.group(1)}">{m.group(2)}</a>' if m.group(3) is None else f'<a class="l2" href="{m.group(1)}">{m.group(2)}</a>',
             md.toc).replace("<ul>","").replace("</ul>","").replace("</li>","").replace("<li>","").replace('class="toc"','')}</nav>
<main>{body}</main></div></body></html>""", encoding="utf-8")

if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".html")
    build(src, dst)
    print(f"OK: {dst}")
