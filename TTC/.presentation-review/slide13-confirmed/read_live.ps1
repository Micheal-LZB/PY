$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class Slide13WordRead { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$wordClass = [Guid]'000209FF-0000-0000-C000-000000000046'
$wordInstance = $null
[Slide13WordRead]::GetActiveObject([ref]$wordClass, [IntPtr]::Zero, [ref]$wordInstance)
$document = @($wordInstance.Documents) | Where-Object { $_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx' }
if (@($document).Count -ne 1) { throw 'Expected one matching open document.' }
$snapshot = @()
for ($i=1; $i -le $document.Paragraphs.Count; $i++) {
    $p = $document.Paragraphs.Item($i)
    $snapshot += [PSCustomObject]@{Index=$i;Start=$p.Range.Start;End=$p.Range.End;Text=$p.Range.Text.TrimEnd([char]13,[char]7)}
}
$snapshot | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath 'E:\PY\TTC\.presentation-review\slide13-confirmed\live-before.json' -Encoding utf8
$document.Content.WordOpenXML | Set-Content -LiteralPath 'E:\PY\TTC\.presentation-review\slide13-confirmed\live-before.xml' -Encoding utf8
$start = ($snapshot | Where-Object {$_.Text -match '^Slide 13\b'}).Index
$stop = ($snapshot | Where-Object {$_.Text -match '^Slide 14\b'}).Index
$snapshot | Where-Object {$_.Index -ge $start -and $_.Index -lt $stop} | ConvertTo-Json -Depth 3
