$ErrorActionPreference='Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class RBackupLiveFinish { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$cls=[Guid]'000209FF-0000-0000-C000-000000000046'
$word=$null
[RBackupLiveFinish]::GetActiveObject([ref]$cls,[IntPtr]::Zero,[ref]$word)
$doc=@($word.Documents) | Where-Object {$_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx'}
if(@($doc).Count -ne 1){throw 'Expected one open main script.'}
$snapshot=@(Get-Content -LiteralPath 'E:\PY\TTC\.presentation-review\r-to-backup\live-before.json' -Raw | ConvertFrom-Json)
$first=$snapshot | Where-Object {$_.Text -match '^Slide 16\b'}
$skipOne=[int]$first.Index+4
$skipTwo=[int]$first.Index+5
$replaceIndex=[int]$first.Index+3
$oldReference='Each vertical line marks one of the equal-total-cost budgets from the previous slide.'
$newReference='Each vertical line marks a setting where the two options have the same total cost.'
$replacement="The question is which option gives higher accuracy at the same total cost. The next figure compares the larger model's greedy answers with the smaller model using extra inference."
$expected=@()
foreach($p in $snapshot){
  if([int]$p.Index -eq $skipOne -or [int]$p.Index -eq $skipTwo){continue}
  $value=[string]$p.Text
  if([int]$p.Index -eq $replaceIndex){$value=$replacement}
  $expected += $value.Replace($oldReference,$newReference)
}
if($doc.Paragraphs.Count -ne $expected.Count){throw 'Unexpected paragraph count; inspect before saving.'}
for($i=1;$i -le $expected.Count;$i++){
  if($doc.Paragraphs.Item($i).Range.Text.TrimEnd([char]13,[char]7) -ne $expected[$i-1]){throw "Unexpected content at paragraph $i; inspect before saving."}
}
$doc.Save()
$doc.ExportAsFixedFormat('E:\PY\TTC\.presentation-review\r-to-backup\main-word.pdf',17)
[PSCustomObject]@{Saved=$doc.Saved;ExpectedTextVerified=$true;OtherTextPreserved=$true} | ConvertTo-Json -Compress
