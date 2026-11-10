$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class Slide13WordEdit { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$wordClass = [Guid]'000209FF-0000-0000-C000-000000000046'
$wordInstance = $null
[Slide13WordEdit]::GetActiveObject([ref]$wordClass, [IntPtr]::Zero, [ref]$wordInstance)
$document = @($wordInstance.Documents) | Where-Object { $_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx' }
if (@($document).Count -ne 1) { throw 'Expected one matching open document.' }
if ($document.TrackRevisions) { throw 'Track changes is enabled; no edits made.' }
$snapshot = @(Get-Content -LiteralPath 'E:\PY\TTC\.presentation-review\slide13-confirmed\live-before.json' -Raw | ConvertFrom-Json)
$start = ($snapshot | Where-Object {$_.Text -match '^Slide 13\b'}).Index
$stop = ($snapshot | Where-Object {$_.Text -match '^Slide 14\b'}).Index
$expected = @($snapshot | Where-Object {$_.Index -ge $start -and $_.Index -lt $stop})
if ($expected.Count -ne 9) { throw 'Slide 13 structure changed; reload before editing.' }
foreach ($p in $expected) {
    if ($document.Paragraphs.Item($p.Index).Range.Text.TrimEnd([char]13,[char]7) -ne $p.Text) { throw 'Slide 13 changed after reading; no edits made.' }
}
$before = @()
for ($i=1; $i -le $document.Paragraphs.Count; $i++) { $before += $document.Paragraphs.Item($i).Range.Text }
$texts = @(
    'Slide 13 Revision Quality and Final Answer Accuracy',
    "Let's start with the left figure. For one question, the model runs four separate chains. Each chain has sixty-four complete answers. At round ten, we check the tenth answer in each chain. We average correctness over the four chains, then over all 500 test questions.",
    'The four chains help us estimate average accuracy. This figure uses no majority vote or ORM selection, either within a chain or across chains. Most improvement happens in early rounds.',
    'Now look at the right figure. Suppose N is eight. Sequential generation makes eight complete answers in one chain, using earlier answers to write the next one. Parallel generation makes eight independent answers. Both use the same revision model.',
    'For sequential generation, we choose from the eight answers in that single chain. Majority voting counts how often each final answer appears. Weighted best-of-N sums ORM scores for matching final answers. We apply the same two rules to the eight independent answers in the parallel case.',
    'Two generation styles and two selection rules give four curves. We check the selected answer for each question and measure accuracy across all 500 questions. Compare sequential and parallel with the same selector: sequential is slightly better. The next slide combines several revision chains and studies how many chains to use and how long to make them.',
    'Conclusions shown on the slide',
    'Most improvement happens in early rounds.',
    'Sequential is slightly better with either selector.'
)
$wordInstance.UndoRecord.StartCustomRecord('Clarify Figure 6 generation and selection')
try {
    for ($j=5; $j -ge 1; $j--) {
        $p = $document.Paragraphs.Item($start+$j)
        $range = $document.Range($p.Range.Start,$p.Range.End-1)
        $range.Text = $texts[$j]
    }
} finally { $wordInstance.UndoRecord.EndCustomRecord() }
$allowed = @(($start+1)..($start+5))
if ($document.Paragraphs.Count -ne $before.Count) { throw 'Unexpected paragraph count change; inspect before saving.' }
for ($i=1; $i -le $document.Paragraphs.Count; $i++) {
    if ($i -notin $allowed -and $document.Paragraphs.Item($i).Range.Text -ne $before[$i-1]) { throw "Unexpected text change outside Slide 13 at paragraph $i." }
}
$document.Save()
$document.ExportAsFixedFormat('E:\PY\TTC\.presentation-review\slide13-confirmed\main-word.pdf',17)
[PSCustomObject]@{Saved=$document.Saved;Updated='Slide 13 only';OtherTextPreserved=$true} | ConvertTo-Json -Compress
