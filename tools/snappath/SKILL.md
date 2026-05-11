---
name: snappath
description: Use when the user wants to get the temporary file path of a clipboard image in the Claude CLI terminal on Windows, without analyzing it. Do NOT use in VSCode or other IDEs. Invoke as /snappath.
---

# snappath

## Overview

Windows 専用スキル。**Claude CLI（ターミナル）専用**。クリップボード上の画像を一時 PNG ファイルに保存し、そのパスだけを返す。

> VSCode などの IDE では画像を直接貼り付けられるため、このスキルは使用しないこと。

```
/snappath
```

画像を他のツールやコマンドに渡したい場合に使用する。

## Steps

### 1. クリップボード画像を一時ファイルに保存

**必ず以下の bash コマンドをそのまま実行すること。PowerShell 構文を bash スクリプトとして書いてはいけない。**

```bash
powershell.exe -STA -Command "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; \$img=[System.Windows.Forms.Clipboard]::GetImage(); if(\$img -eq \$null){Write-Error 'No image in clipboard';exit 1}; \$p=\"\$env:TEMP\snap_\$([guid]::NewGuid()).png\"; \$img.Save(\$p,[System.Drawing.Imaging.ImageFormat]::Png); Write-Output \$p"
```

### 2. パスを返す

出力されたファイルパスをそのままユーザーに返す。

## Example Output

```
C:\Users\xxx\AppData\Local\Temp\claude_3f2a1b4c-xxxx.png
```

## Error Handling

| エラー | 対処 |
|--------|------|
| `No image found in clipboard` | 画像をクリップボードにコピーしてから再実行するよう案内する |
| PowerShell 実行エラー | エラーメッセージをそのまま表示する |

## Requirements

- Windows OS
- PowerShell
