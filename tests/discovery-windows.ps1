# Offline parser tests: compile the exact C# used by the copyable Windows command.
$ErrorActionPreference = 'Stop'
$source = Get-Content -Raw (Join-Path $PSScriptRoot '../web/discovery-help/windows.ps1')
$tokens = $null; $errors = $null
[System.Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$errors) | Out-Null
if ($errors.Count) { throw ($errors | Out-String) }
$cs = [regex]::Match($source, "(?s)Add-Type -TypeDefinition @'\r?\n(.*?)\r?\n'@").Groups[1].Value
Add-Type -TypeDefinition $cs
function Assert($condition, $message) { if (-not $condition) { throw $message } }
$packet = [Convert]::FromBase64String('AACEAAAAAAMAAAAABF9odWUEX3RjcAVsb2NhbAAADAABAAAAeAAjEUh1ZSBCcmlkZ2UgLSBUZXN0BF9odWUEX3RjcAVsb2NhbAARSHVlIEJyaWRnZSAtIFRlc3QEX2h1ZQRfdGNwBWxvY2FsAAAhAAEAAAB4ABIAAAAAAbsEdGVzdAVsb2NhbAAEdGVzdAVsb2NhbAAAAQABAAAAeAAEwKgCCg==')
$records = New-Object Hue2LoxLocalDiscovery+Records
[Hue2LoxLocalDiscovery]::Parse($packet,$records)
Assert ($records.Instances.Count -eq 1) 'PTR instance'
Assert ($records.Targets['Hue Bridge - Test._hue._tcp.local'] -eq 'test.local') 'SRV target'
Assert ($records.Addresses['test.local'] -eq '192.168.2.10') 'IPv4 address'
[Hue2LoxLocalDiscovery]::Parse($packet,$records)
Assert ($records.Instances.Count -eq 1) 'deduplication'
# Compression loop, truncated packet, bogus label, excessive record count.
$loop = [byte[]](0,0,132,0,0,0,0,1,0,0,0,0,192,12)
$invalid = [byte[]](0,0,132,0,0,0,0,1,0,0,0,0,127)
$large = [byte[]](0,0,132,0,0,0,2,0,0,0,0,0)
foreach ($bad in @($loop, $invalid, $large, [byte[]]($packet[0..($packet.Length-2)]))) {
    $empty = New-Object Hue2LoxLocalDiscovery+Records
    $rejected = $false
    try { [Hue2LoxLocalDiscovery]::Parse($bad,$empty) } catch { $rejected = $true }
    Assert $rejected 'Malformed packet accepted'
    Assert ($empty.Instances.Count -eq 0) 'Partial state escaped from malformed packet'
}
$query = [Hue2LoxLocalDiscovery]::Query('_hue._tcp.local',12)
Assert ($query[$query.Length-2] -eq 128 -and $query[$query.Length-1] -eq 1) 'unicast response requested'
# TTL-zero goodbye records.
$goodbye = [byte[]]$packet.Clone()
# First record TTL is immediately after owner + type/class.
$ttl = 12 + 17 + 4
0..3 | ForEach-Object { $goodbye[$ttl+$_] = 0 }
$empty = New-Object Hue2LoxLocalDiscovery+Records
[Hue2LoxLocalDiscovery]::Parse($goodbye,$empty)
Assert ($empty.Instances.Count -eq 0) 'TTL zero PTR should be ignored'
Write-Host 'Windows discovery: syntax, compilation, PTR/SRV/A, deduplication, malformed packets and query passed.'
