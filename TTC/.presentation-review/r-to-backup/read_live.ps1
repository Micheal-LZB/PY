$ErrorActionPreference='Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class RBackupLiveRead { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$cls=[Guid]'000209FF-0000-0000-C000-000000000046'
$word=$null
[RBackupLiveRead]::GetActiveObject([ref]$cls,[IntPtr]::Zero,[ref]$word)
$doc=@($word.Documents) | Where-Object {$_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx'}
if(@($doc).Count -ne 1){throw 'Expected one open main script.'}
$snapshot=@()
for($i=1;$i -le $doc.Paragraphs.Count;$i++){
  $p=$doc.Paragraphs.Item($i)
  $snapshot += [PSCustomObject]@{Index=$i;Start=$p.Range.Start;End=$p.Range.End;Text=$p.Range.Text.TrimEnd([char]13,[char]7)}
}
$snapshot | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath 'E:\PY\TTC\.presentation-review\r-to-backup\live-before.json' -Encoding utf8
$doc.Content.WordOpenXML | Set-Content -LiteralPath 'E:\PY\TTC\.presentation-review\r-to-backup\live-before.xml' -Encoding utf8
$first=($snapshot | Where-Object {$_.Text -match '^Slide 16\b'}).Index
$last=($snapshot | Where-Object {$_.Text -match '^Slide 18\b'}).Index
[PSCustomObject]@{Saved=$doc.Saved;TrackRevisions=$doc.TrackRevisions;ReadOnly=$doc.ReadOnly} | ConvertTo-Json -Compress
$snapshot | Where-Object {$_.Index -ge $first -and $_.Index -lt $last} | ConvertTo-Json -Depth 3
