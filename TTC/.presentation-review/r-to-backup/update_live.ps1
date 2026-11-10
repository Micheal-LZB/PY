$ErrorActionPreference='Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class RBackupLiveEdit { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$cls=[Guid]'000209FF-0000-0000-C000-000000000046'
$word=$null
[RBackupLiveEdit]::GetActiveObject([ref]$cls,[IntPtr]::Zero,[ref]$word)
$doc=@($word.Documents) | Where-Object {$_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx'}
if(@($doc).Count -ne 1){throw 'Expected one open main script.'}
if($doc.TrackRevisions -or $doc.ReadOnly){throw 'Document is not available for an ordinary edit.'}
$snapshot=@(Get-Content -LiteralPath 'E:\PY\TTC\.presentation-review\r-to-backup\live-before.json' -Raw | ConvertFrom-Json)
$first=$snapshot | Where-Object {$_.Text -match '^Slide 16\b'}
$next=$snapshot | Where-Object {$_.Text -match '^Slide 17\b'}
$last=$snapshot | Where-Object {$_.Text -match '^Slide 18\b'}
foreach($p in @($snapshot | Where-Object {$_.Index -ge $first.Index -and $_.Index -lt $last.Index})){
  if($doc.Paragraphs.Item($p.Index).Range.Text.TrimEnd([char]13,[char]7) -ne $p.Text){throw 'The selected section changed; reload before editing.'}
}
$before=@()
for($i=1;$i -le $doc.Paragraphs.Count;$i++){$before += $doc.Paragraphs.Item($i).Range.Text.TrimEnd([char]13,[char]7)}
$oldReference='Each vertical line marks one of the equal-total-cost budgets from the previous slide.'
$newReference='Each vertical line marks a setting where the two options have the same total cost.'
$referenceIndex=($snapshot | Where-Object {$_.Text.Contains($oldReference)}).Index
if(-not $referenceIndex){throw 'Expected result-figure reference not found.'}
$replacement="The question is which option gives higher accuracy at the same total cost. The next figure compares the larger model's greedy answers with the smaller model using extra inference."
$word.UndoRecord.StartCustomRecord('Move R explanation to backup')
try {
  $p=$doc.Paragraphs.Item($referenceIndex)
  $range=$doc.Range($p.Range.Start,$p.Range.End-1)
  $range.Text=$before[$referenceIndex-1].Replace($oldReference,$newReference)
  $from=$doc.Paragraphs.Item($first.Index+4).Range.Start
  $to=$doc.Paragraphs.Item($next.Index).Range.Start
  [void]$doc.Range($from,$to).Delete()
  $p=$doc.Paragraphs.Item($first.Index+3)
  $range=$doc.Range($p.Range.Start,$p.Range.End-1)
  $range.Text=$replacement
} finally {$word.UndoRecord.EndCustomRecord()}
$expected=@()
for($i=1;$i -le $before.Count;$i++){
  if($i -in @(($first.Index+4),($first.Index+5))){continue}
  $value=$before[$i-1]
  if($i -eq $first.Index+3){$value=$replacement}
  if($i -eq $referenceIndex){$value=$value.Replace($oldReference,$newReference)}
  $expected += $value
}
if($doc.Paragraphs.Count -ne $expected.Count){throw 'Unexpected paragraph count change.'}
for($i=1;$i -le $expected.Count;$i++){
  if($doc.Paragraphs.Item($i).Range.Text.TrimEnd([char]13,[char]7) -ne $expected[$i-1]){throw "Unexpected text change at paragraph $i."}
}
$doc.Save()
$doc.ExportAsFixedFormat('E:\PY\TTC\.presentation-review\r-to-backup\main-word.pdf',17)
[PSCustomObject]@{Saved=$doc.Saved;Updated='Slide 16 and result-figure transition';OtherTextPreserved=$true} | ConvertTo-Json -Compress
