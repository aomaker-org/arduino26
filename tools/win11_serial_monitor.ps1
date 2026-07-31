# file: tools/win11_serial_monitor.ps1
# Purpose: Native Windows 11 PowerShell Serial Monitor for COM Ports (e.g. COM5)
# Usage from WSL bash: pwsh.exe -File tools/win11_serial_monitor.ps1 -Port COM5 -Baud 115200
# Usage from PowerShell: .\tools\win11_serial_monitor.ps1 -Port COM5 -Baud 115200

param(
    [string]$Port = "COM5",
    [int]$Baud = 115200
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Arduino26 Native Windows 11 Serial Monitor            " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "[*] Target Port : $Port" -ForegroundColor Yellow
Write-Host "[*] Baud Rate   : $Baud" -ForegroundColor Yellow
Write-Host "[*] Exit        : Press Ctrl+C to disconnect" -ForegroundColor Yellow
Write-Host "----------------------------------------------------------"

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, None, 8, One
    $sp.Encoding = [System.Text.Encoding]::UTF8
    $sp.ReadTimeout = 1000
    $sp.WriteTimeout = 1000
    $sp.Open()
    Write-Host "[+] Successfully connected to $Port." -ForegroundColor Green
} catch {
    Write-Host "[X] Error connecting to $Port : $_" -ForegroundColor Red
    Write-Host "[i] Available Ports on Host:" -ForegroundColor Yellow
    [System.IO.Ports.SerialPort]::GetPortNames() | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

$LogDir = Join-Path (Get-Location) "agy\log"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$StartDt = Get-Date
$BaseTs = $StartDt.ToString("yyMMdd_HHmmss")
$Seq = 1
do {
    $SessionFileName = "serial_telemetry_${BaseTs}_$(("{0:D3}" -f $Seq)).log"
    $SessionLogPath = Join-Path $LogDir $SessionFileName
    $Seq++
} while (Test-Path $SessionLogPath)

$MasterLogPath = Join-Path $LogDir "serial_telemetry.log"
Write-Host "[*] Session Log     : $SessionFileName" -ForegroundColor Yellow

$Header = @"
==========================================================
Arduino26 Telemetry Log Started: $($StartDt.ToString("yyyy-MM-dd HH:mm:ss K"))
Target Port : $Port | Baud Rate: $Baud
Log File    : $SessionFileName
==========================================================
"@

Add-Content -Path $SessionLogPath -Value $Header -Encoding UTF8
Add-Content -Path $MasterLogPath -Value $Header -Encoding UTF8

$LineCount = 0

try {
    while ($sp.IsOpen) {
        try {
            $line = $sp.ReadLine()
            if ($line) {
                $LineCount++
                $Now = Get-Date
                $ElapsedSec = [int]($Now - $StartDt).TotalSeconds
                $Hours = [math]::Floor($ElapsedSec / 3600)
                $Minutes = [math]::Floor(($ElapsedSec % 3600) / 60)
                $Seconds = $ElapsedSec % 60
                $DatePrefix = $Now.ToString("yyMMdd")
                $TimePrefix = "+$(("{0:D2}" -f $Hours)):$(("{0:D2}" -f $Minutes)):$(("{0:D2}" -f $Seconds))"
                
                $entry = "[$DatePrefix $TimePrefix] $line"
                Write-Host $entry -ForegroundColor White
                Add-Content -Path $SessionLogPath -Value $entry -Encoding UTF8
                Add-Content -Path $MasterLogPath -Value $entry -Encoding UTF8
            }
        } catch [TimeoutException] {
            # Timeout is expected when no data arrives
        }
    }
} finally {
    $EndDt = Get-Date
    $DurationSec = [int]($EndDt - $StartDt).TotalSeconds
    $DH = [math]::Floor($DurationSec / 3600)
    $DM = [math]::Floor(($DurationSec % 3600) / 60)
    $DS = $DurationSec % 60
    $DurStr = "$(("{0:D2}" -f $DH)):$(("{0:D2}" -f $DM)):$(("{0:D2}" -f $DS))"

    $Footer = @"
==========================================================
Arduino26 Telemetry Log Ended: $($EndDt.ToString("yyyy-MM-dd HH:mm:ss K"))
Duration     : $DurStr | Total Lines: $LineCount
==========================================================
"@
    Add-Content -Path $SessionLogPath -Value $Footer -Encoding UTF8
    Add-Content -Path $MasterLogPath -Value $Footer -Encoding UTF8

    if ($sp.IsOpen) {
        $sp.Close()
        Write-Host "[*] Serial port $Port closed cleanly." -ForegroundColor Yellow
    }
}

# file tools/win11_serial_monitor.ps1 ends
