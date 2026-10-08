param(
    [Parameter(Mandatory=$true)][string]$LogPath,
    [Parameter(Mandatory=$true)][string]$CommandPath
)

$ErrorActionPreference = 'SilentlyContinue'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Append-Command([string]$line) {
    try {
        [System.IO.File]::AppendAllText($CommandPath, $line + [Environment]::NewLine, $utf8NoBom)
    } catch {}
}

# -----------------------------------------------------------------------------
# Debug-console mode (F10 + R)
# -----------------------------------------------------------------------------
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = 'Luck be a Landlord - Archipelago Debug'
try {
    $size = $Host.UI.RawUI.WindowSize
    $size.Width = [Math]::Min(160, $Host.UI.RawUI.MaxPhysicalWindowSize.Width)
    $size.Height = [Math]::Min(45, $Host.UI.RawUI.MaxPhysicalWindowSize.Height)
    $Host.UI.RawUI.WindowSize = $size
} catch {}

function Show-Header {
    Write-Host 'Luck be a Landlord - Archipelago Debug' -ForegroundColor Green
    Write-Host 'Only the current AP connection is shown.' -ForegroundColor DarkGray
    Write-Host 'Type help for commands. Type close to close only this window.' -ForegroundColor DarkGray
    Write-Host ('Log: ' + $LogPath) -ForegroundColor DarkGray
    Write-Host ''
}

Show-Header
$seen = 0
if (Test-Path -LiteralPath $LogPath) {
    try {
        $startupLines = @(Get-Content -LiteralPath $LogPath -Encoding UTF8)
        $lastMarker = -1
        for ($i = 0; $i -lt $startupLines.Count; $i++) {
            if ([string]$startupLines[$i] -eq '=== AP CONNECTED SESSION ===') { $lastMarker = $i }
        }
        if ($lastMarker -ge 0) { $seen = $lastMarker } else { $seen = $startupLines.Count }
    } catch {}
}
$buffer = ''

function Clear-PromptLine {
    try {
        $width = [Math]::Max(20, [Console]::WindowWidth - 1)
        [Console]::Write("`r" + (' ' * $width) + "`r")
    } catch { [Console]::Write("`r") }
}
function Draw-Prompt { [Console]::Write('> ' + $script:buffer) }

Draw-Prompt
while ($true) {
    if (Test-Path -LiteralPath $LogPath) {
        try {
            $lines = @(Get-Content -LiteralPath $LogPath -Encoding UTF8)
            if ($lines.Count -lt $seen) { $seen = 0 }
            if ($lines.Count -gt $seen) {
                Clear-PromptLine
                for ($i = $seen; $i -lt $lines.Count; $i++) {
                    $line = [string]$lines[$i]
                    if ($line -eq '=== AP CONNECTED SESSION ===') { Clear-Host; Show-Header; continue }
                    if ($line -match 'ERROR|REFUSED|CLOSE REQUEST|FAILED') { Write-Host $line -ForegroundColor Red }
                    elseif ($line -match 'RECEIVED ITEM|LOCATION|HOOK|CONNECTED|RoomInfo|Connected|AP state sync|SHINY COIN') { Write-Host $line -ForegroundColor Cyan }
                    elseif ($line -match 'RAW <-|RAW ->') { Write-Host $line -ForegroundColor DarkGray }
                    else { Write-Host $line }
                }
                $seen = $lines.Count
                Draw-Prompt
            }
        } catch {}
    }

    while ([Console]::KeyAvailable) {
        $key = [Console]::ReadKey($true)
        if ($key.Key -eq [ConsoleKey]::Enter) {
            Clear-PromptLine
            Write-Host ('> ' + $buffer) -ForegroundColor Green
            $command = $buffer.Trim()
            $buffer = ''
            if ($command.Length -gt 0) {
                Append-Command $command
                if ($command.ToLowerInvariant() -eq 'close' -or $command.ToLowerInvariant() -eq 'exit') {
                    Start-Sleep -Milliseconds 250
                    exit 0
                }
            }
            Draw-Prompt
        } elseif ($key.Key -eq [ConsoleKey]::Backspace) {
            if ($buffer.Length -gt 0) {
                $buffer = $buffer.Substring(0, $buffer.Length - 1)
                Clear-PromptLine; Draw-Prompt
            }
        } elseif ($key.Key -eq [ConsoleKey]::Escape) {
            $buffer = ''; Clear-PromptLine; Draw-Prompt
        } elseif (-not [char]::IsControl($key.KeyChar)) {
            $buffer += $key.KeyChar
            [Console]::Write($key.KeyChar)
        }
    }
    Start-Sleep -Milliseconds 75
}
