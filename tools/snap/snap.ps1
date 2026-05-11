param(
    [string]$mode = "run",   # run / path
    [string]$prompt = ""
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$img = [System.Windows.Forms.Clipboard]::GetImage()

if ($img -eq $null) {
    Write-Error "No image found in clipboard"
    exit 1
}

$path = "$env:TEMP\claude_$([guid]::NewGuid()).png"
$img.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)

if ($mode -eq "path") {
    Write-Output $path
    exit 0
}

if ([string]::IsNullOrWhiteSpace($prompt)) {
    $prompt = "Analyze this image"
}

claude $prompt $path
