---
name: snap
description: Use when the user wants to analyze a screenshot or clipboard image in the Claude CLI terminal on Windows. Do NOT use in VSCode or other IDEs where images can be pasted directly. Invoke as /snap [prompt].
---

# snap

## Overview

Windows 専用スキル。**Claude CLI（ターミナル）専用**。Snipping Tool などでクリップボードにコピーした画像を、Claude CLI から直接分析する。

> VSCode などの IDE では画像を直接貼り付けられるため、このスキルは使用しないこと。

```
/snap [prompt]
```

引数を省略した場合は `Analyze this image` をデフォルトプロンプトとして使用する。

## Steps

### 1. クリップボード画像を一時ファイルに保存

**必ず以下の bash コマンドをそのまま実行すること。PowerShell 構文を bash スクリプトとして書いてはいけない。**

```bash
powershell.exe -STA -Command "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; \$img=[System.Windows.Forms.Clipboard]::GetImage(); if(\$img -eq \$null){Write-Error 'No image in clipboard';exit 1}; \$p=\"\$env:TEMP\snap_\$([guid]::NewGuid()).png\"; \$img.Save(\$p,[System.Drawing.Imaging.ImageFormat]::Png); Write-Output \$p"
```

成功すると一時ファイルのパスが出力される（例：`C:\Users\xxx\AppData\Local\Temp\snap_xxx.png`）。

### 2. 画像を読み込む

出力されたパスを `Read` ツールで読み込む。

### 3. 分析する

ユーザーが指定したプロンプトで画像を分析し、結果を返す。

## Error Handling

| エラー | 対処 |
|--------|------|
| `No image found in clipboard` | 画像をクリップボードにコピーしてから再実行するよう案内する |
| PowerShell 実行エラー | エラーメッセージをそのまま表示する |

## Requirements

- Windows OS
- PowerShell
