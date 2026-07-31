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
    $sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, None, 8, One
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

try {
    while ($sp.IsOpen) {
        try {
            $line = $sp.ReadLine()
            if ($line) {
                $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                Write-Host "[$ts] $line" -ForegroundColor White
            }
        } catch [TimeoutException] {
            # Timeout is expected when no data arrives
        }
    }
} finally {
    if ($sp.IsOpen) {
        $sp.Close()
        Write-Host "[*] Serial port $Port closed cleanly." -ForegroundColor Yellow
    }
}

# file tools/win11_serial_monitor.ps1 ends
