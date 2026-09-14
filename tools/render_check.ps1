<#
.SYNOPSIS
  Build pilots (or take a report folder), open each in Power BI Desktop, refresh, and capture every page.
  Then compare pilots with the committed screenshots.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\render_check.ps1
  powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Purpose matrix -Theme midnight -Lang ko
  powershell -ExecutionPolicy Bypass -File tools\render_check.ps1 -Dir examples\StoreKPI

.NOTES
  Why: Microsoft's validator checks the files, not the screen. Files that pass can still render wrong
  (clipped labels, doubled units, an ignored filter), and older Desktop versions render the same files differently (#1).

  Output: out\render\<folder>\NN-<page>.png (the 1280x720 page), out\render\sheet.png (all pages at once),
  and a changed-pixel share per page against templates\<purpose>\screenshots (navy + en pilots only). Needs: pip install pillow.

  Uses the Microsoft Store Desktop when installed (it keeps itself up to date). Works with any Desktop display
  language: controls are found by class and position, not by their labels. Tabs are switched through UI Automation,
  so the mouse isn't moved. Only the Desktop windows this script opens are closed.
#>
param(
  [ValidateSet("all", "dashboard", "table", "matrix", "deepdive")] [string]$Purpose = "all",
  [ValidateSet("navy", "paper", "midnight")] [string]$Theme = "navy",
  [string]$Lang = "en",
  [string]$Dir = "",
  [int]$TimeoutSeconds = 180
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$outRoot = Join-Path $repo "out\render"
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Drawing
Add-Type @'
using System; using System.Runtime.InteropServices;
public static class RenderCap {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
}
'@
$AE = [System.Windows.Automation.AutomationElement]
$CT = [System.Windows.Automation.ControlType]
$failed = @()   # reports that never opened

function Find-Type($el, $type) {
  $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $type)
  @($el.FindAll([System.Windows.Automation.TreeScope]::Descendants, $cond))
}
function Invoke-Element($el) {
  $p = $null
  if ($el.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$p)) { $p.Select(); return }
  if ($el.TryGetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern, [ref]$p)) { $p.Invoke() }
}
function Get-PageHost($win) {   # the report canvas: class names are the same in every display language
  Find-Type $win $CT::Group | Where-Object { $_.Current.ClassName -match 'visualContainerHost' } | Select-Object -First 1
}
function Get-DesktopExe {
  $store = Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps\PBIDesktopStore.exe"
  if (Test-Path $store) { return $store }
  $msi = Join-Path $env:ProgramFiles "Microsoft Power BI Desktop\bin\PBIDesktop.exe"
  if (Test-Path $msi) {
    Write-Warning "Microsoft Store Desktop not found; using installer version $((Get-Item $msi).VersionInfo.FileVersion). Versions older than 2.157 cut off labels (#1)."
    return $msi
  }
  throw "Power BI Desktop was not found. Install it from the Microsoft Store."
}

function Save-Page($proc, $file) {
  $h = $proc.MainWindowHandle
  if ([RenderCap]::IsIconic($h)) { [RenderCap]::ShowWindow($h, 9) | Out-Null; Start-Sleep -Milliseconds 800 }
  $r = New-Object RenderCap+RECT
  [RenderCap]::GetWindowRect($h, [ref]$r) | Out-Null
  $shot = New-Object System.Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T)
  $g = [System.Drawing.Graphics]::FromImage($shot)
  $hdc = $g.GetHdc(); [RenderCap]::PrintWindow($h, $hdc, 2) | Out-Null; $g.ReleaseHdc($hdc); $g.Dispose()
  # "Fit to page" centres the 16:9 page inside the canvas host
  $b = (Get-PageHost ($AE::FromHandle($h))).Current.BoundingRectangle
  $pw = [Math]::Min($b.Width, $b.Height * 16 / 9); $ph = $pw * 9 / 16
  $src = New-Object System.Drawing.Rectangle ([int]($b.X + ($b.Width - $pw) / 2 - $r.L)), ([int]($b.Y + ($b.Height - $ph) / 2 - $r.T)), ([int]$pw), ([int]$ph)
  $page = New-Object System.Drawing.Bitmap 1280, 720
  $g = [System.Drawing.Graphics]::FromImage($page)
  $g.InterpolationMode = 'HighQualityBicubic'
  $g.DrawImage($shot, (New-Object System.Drawing.Rectangle 0, 0, 1280, 720), $src, 'Pixel')
  $g.Dispose(); $shot.Dispose()
  $page.Save($file, [System.Drawing.Imaging.ImageFormat]::Png); $page.Dispose()
}

function Test-Report($exe, $dir) {
  $pbip = Get-ChildItem $dir -Filter *.pbip | Select-Object -First 1
  if (-not $pbip) { Write-Warning "no .pbip in $dir"; return }
  $name = $pbip.BaseName
  $pagesDir = Join-Path $dir "$name.Report\definition\pages"
  $order = (Get-Content (Join-Path $pagesDir "pages.json") -Raw -Encoding UTF8 | ConvertFrom-Json).pageOrder
  $titles = foreach ($id in $order) { (Get-Content (Join-Path $pagesDir "$id\page.json") -Raw -Encoding UTF8 | ConvertFrom-Json).displayName }
  $before = @(Get-Process PBIDesktop -ErrorAction SilentlyContinue | ForEach-Object Id)
  # 이전 캡처를 먼저 지운다: 열기에 실패했는데 옛 캡처로 "일치"라고 보고하지 않게
  $dest = Join-Path $outRoot (Split-Path $dir -Leaf)
  New-Item -ItemType Directory -Force $dest | Out-Null
  Get-ChildItem $dest -Filter *.png | Remove-Item

  Start-Process -FilePath $exe -ArgumentList "`"$($pbip.FullName)`""
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds); $proc = $null; $win = $null
  while ((Get-Date) -lt $deadline -and -not $win) {
    Start-Sleep -Seconds 3
    $proc = Get-Process PBIDesktop -ErrorAction SilentlyContinue | Where-Object { $_.Id -notin $before -and $_.MainWindowTitle -like "*$name*" } | Select-Object -First 1
    if ($proc) { $w = $AE::FromHandle($proc.MainWindowHandle); if (Get-PageHost $w) { $win = $w } }
  }
  if (-not $win) {
    Write-Warning "$name did not open within $TimeoutSeconds s: the model or report failed to load (open it in Desktop to read the error)"
    $script:failed += $name
    Get-Process PBIDesktop -ErrorAction SilentlyContinue | Where-Object { $_.Id -notin $before } | Stop-Process -Force
    return
  }

  # First open has no data yet: the yellow bar's first button refreshes (class 'action-button' in every language)
  Start-Sleep -Seconds 5
  $refresh = Find-Type $win $CT::Button | Where-Object { $_.Current.ClassName -match '^action-button' } | Select-Object -First 1
  if ($refresh) {
    $label = $refresh.Current.Name
    Invoke-Element $refresh
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do { Start-Sleep -Seconds 3
      $still = Find-Type $win $CT::Button | Where-Object { $_.Current.ClassName -match '^action-button' -and $_.Current.Name -eq $label }
    } while ($still -and (Get-Date) -lt $deadline)
    Start-Sleep -Seconds 15
  }

  # Report view = the top tab of the left rail; page tabs carry 'thumbnail-container'
  $tabs = Find-Type $win $CT::TabItem
  $reportView = $tabs | Where-Object { $_.Current.BoundingRectangle.X -lt 8 -and $_.Current.BoundingRectangle.Width -le 48 } |
    Sort-Object { $_.Current.BoundingRectangle.Y } | Select-Object -First 1
  $pageTabs = @($tabs | Where-Object { $_.Current.ClassName -match 'thumbnail-container' } | Sort-Object { $_.Current.BoundingRectangle.X })
  for ($i = 0; $i -lt $pageTabs.Count; $i++) {
    Invoke-Element $pageTabs[$i]; Start-Sleep -Seconds 2
    if ($reportView) { Invoke-Element $reportView }   # moves focus off the tab so its tooltip doesn't cover the page
    Start-Sleep -Seconds 4
    $title = if ($i -lt $titles.Count) { $titles[$i] } else { "page" }
    $safe = ($title -replace '[^\p{L}\p{N}]+', '_').Trim('_')
    Save-Page $proc (Join-Path $dest ("{0:D2}-{1}.png" -f ($i + 1), $safe))
    "  captured $(Split-Path $dir -Leaf) / $title"
  }
  Stop-Process -Id $proc.Id -Force
  Start-Sleep -Seconds 4
}

$exe = Get-DesktopExe
$py = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }
Push-Location $repo
try {
  if ($Dir) {
    Test-Report $exe (Resolve-Path $Dir).Path
  } else {
    $qs = @("tools\quickstart.py", "--theme", $Theme, "--lang", $Lang)
    $qs += if ($Purpose -eq "all") { @("--all") } else { @("--purpose", $Purpose) }
    & $py @qs | Select-Object -First 1
    $purposes = if ($Purpose -eq "all") { @("dashboard", "table", "matrix", "deepdive") } else { @($Purpose) }
    foreach ($p in $purposes) { Test-Report $exe (Join-Path $repo "out\$p-$Theme-$Lang") }
  }
  & $py tools\render_report.py $outRoot
  $reportExit = $LASTEXITCODE
} finally { Pop-Location }
if ($failed.Count) { Write-Host "FAILED to open in Desktop: $($failed -join ', ')"; exit 1 }
exit $reportExit
