# file: tools/monitor_win_ports.ps1
# Purpose: Real-time loop monitoring Windows host COM port changes (detect bootloader port)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "      Monitoring Windows Host COM Ports (60s loop)" -ForegroundColor Cyan
Write-Host "      Press the physical RESET button on the Leonardo now!" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$lastPorts = @()
$startTime = Get-Date
$duration = New-TimeSpan -Seconds 60

while (((Get-Date) - $startTime) -lt $duration) {
    # Query current COM ports via Net SerialPort
    $currentPorts = [System.IO.Ports.SerialPort]::GetPortNames() | Sort-Object
    
    # Check for additions
    foreach ($p in $currentPorts) {
        if ($lastPorts -notcontains $p) {
            $ts = (Get-Date).ToString("HH:mm:ss.fff")
            Write-Host "[$ts] [+] NEW PORT DETECTED: $p" -ForegroundColor Green
            
            # Fetch PnP friendly name for this port
            $dev = Get-PnpDevice -PresentOnly | Where-Object { $_.FriendlyName -like "*($p)*" } | Select-Object -First 1
            if ($dev) {
                Write-Host "      Device: $($dev.FriendlyName)" -ForegroundColor Gray
            }
        }
    }
    
    # Check for removals
    foreach ($p in $lastPorts) {
        if ($currentPorts -notcontains $p) {
            $ts = (Get-Date).ToString("HH:mm:ss.fff")
            Write-Host "[$ts] [-] PORT REMOVED: $p" -ForegroundColor Red
        }
    }
    
    $lastPorts = $currentPorts
    Start-Sleep -Milliseconds 150
}

Write-Host "`n[*] Monitoring finished." -ForegroundColor Cyan
# file tools/monitor_win_ports.ps1 ends
