<#
  shot.ps1 - render an HTML or SVG to a PNG that is not clipped at the bottom.

  Why this exists: chromium --headless=new renders into a viewport that can be
  ~80px shorter than --window-size, so asking for the target height clips the
  last rows (this cut the raster-to-svg banner and a report table on 2026-11-23).
  This script renders taller, finds the last row that is not page background,
  and crops to it.

  Usage:
    pwsh -File shot.ps1 -In page.html -Width 1200 -Height 400 -Out banner.png
    pwsh -File shot.ps1 -In demo.html  -Width 1400 -Height 0   -Out report.png   # 0 = auto height
    pwsh -File shot.ps1 -In banner.svg -Width 1200 -Height 400 -Out banner.png -Bg "#1a0f0c"

  Chromium: -Chrome <path>, else the CHROME env var, else a Playwright cache path.
  Exit: 0 ok, 1 short page or possible clipping (image still written), 2 error.
#>
param(
  [Parameter(Mandatory = $true)][string]$In,
  [int]$Width = 1200,
  [int]$Height = 400,
  [string]$Out = "",
  [string]$Bg = "",
  [string]$Chrome = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

if (-not (Test-Path $In)) { Write-Error "input not found: $In"; exit 2 }
$src = (Resolve-Path $In).Path
if (-not $Out) { $Out = [System.IO.Path]::ChangeExtension($src, ".png") }
$Out = [System.IO.Path]::GetFullPath($Out)

if (-not $Chrome) { $Chrome = $env:CHROME }
if (-not $Chrome) {
  $root = Join-Path $env:LOCALAPPDATA "ms-playwright"
  $cands = (Get-ChildItem $root -Directory -Filter "chromium-*" -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending | ForEach-Object { Join-Path (Join-Path $_.FullName "chrome-win64") "chrome.exe" })
  $Chrome = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Chrome -or -not (Test-Path $Chrome)) { Write-Error "chromium not found; pass -Chrome"; exit 2 }

# an SVG needs a zero-margin page, otherwise the browser adds margins and a white page
$page = $src
$tmp = Join-Path $env:TEMP ("shot-" + [guid]::NewGuid().ToString("N") + ".html")
if ([System.IO.Path]::GetExtension($src) -eq ".svg") {
  $bg = if ($Bg) { $Bg } else { "#0f1216" }
  $svg = Get-Content $src -Raw -Encoding UTF8
  $html = "<!doctype html><html><head><meta charset='utf-8'><style>html,body{margin:0;padding:0;background:" + $bg + ";overflow:hidden}svg{display:block}</style></head><body>" + $svg + "</body></html>"
  Set-Content -Path $tmp -Value $html -Encoding UTF8
  $page = $tmp
}

$renderH = if ($Height -gt 0) { $Height + 300 } else { 2000 }
$raw = Join-Path $env:TEMP ("shot-" + [guid]::NewGuid().ToString("N") + ".png")
$url = "file:///" + $page.Replace('\', '/').Replace(' ', '%20')

& $Chrome --headless=new --disable-gpu --hide-scrollbars "--window-size=$Width,$renderH" --virtual-time-budget=5000 "--screenshot=$raw" $url 2>$null | Out-Null
if (-not (Test-Path $raw)) { Write-Error "chromium produced no screenshot"; exit 2 }

$img = [System.Drawing.Bitmap]::FromFile($raw)
$bgPixel = $img.GetPixel(1, $img.Height - 1)
$last = $img.Height - 1
for ($y = $img.Height - 1; $y -ge 0; $y--) {
  $hit = $false
  for ($x = 0; $x -lt $img.Width; $x += 4) {
    $c = $img.GetPixel($x, $y)
    if ([math]::Abs($c.R - $bgPixel.R) + [math]::Abs($c.G - $bgPixel.G) + [math]::Abs($c.B - $bgPixel.B) -gt 14) { $hit = $true; break }
  }
  if ($hit) { $last = $y; break }
}

$code = 0
if ($Height -gt 0) {
  # a fixed canvas: keep exactly -Height, and warn when content runs past it
  $cropH = $Height
  if ($last -ge $Height) {
    Write-Warning "content extends past the requested height and will be clipped; use -Height 0 for auto, or a taller canvas"
    $code = 1
  }
} else {
  # auto height: crop to the last content row plus 24px
  $cropH = [math]::Min($img.Height, $last + 24)
  if ($last -ge ($img.Height - 2)) {
    Write-Warning "content reaches the last rendered row ($($img.Height - 1)px) - increase the auto ceiling"
    $code = 1
  }
}

$dst = New-Object System.Drawing.Bitmap $img.Width, $cropH
$g = [System.Drawing.Graphics]::FromImage($dst)
$g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, $img.Width, $cropH), (New-Object System.Drawing.Rectangle 0, 0, $img.Width, $cropH), [System.Drawing.GraphicsUnit]::Pixel)
$dst.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$w = $img.Width
$g.Dispose(); $dst.Dispose(); $img.Dispose()
Remove-Item $raw -Force -ErrorAction SilentlyContinue
if ($page -ne $src) { Remove-Item $page -Force -ErrorAction SilentlyContinue }

Write-Output ($Out + "  " + $w + "x" + $cropH)
exit $code
