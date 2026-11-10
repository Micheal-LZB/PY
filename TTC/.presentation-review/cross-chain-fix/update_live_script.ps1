$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public static class TtcWordRunning { [DllImport("oleaut32.dll", PreserveSig=false)] public static extern void GetActiveObject(ref Guid rclsid, IntPtr reserved, [MarshalAs(UnmanagedType.IUnknown)] out object instance); }'
$wordClass = [Guid]'000209FF-0000-0000-C000-000000000046'
$wordInstance = $null
[TtcWordRunning]::GetActiveObject([ref]$wordClass, [IntPtr]::Zero, [ref]$wordInstance)
$document = @($wordInstance.Documents) | Where-Object { $_.FullName -eq 'E:\PY\TTC\presentation\presentation paper\test-time-compute-main-script.docx' }
if (@($document).Count -ne 1) { throw 'Expected one matching open document.' }
if ($document.TrackRevisions) { throw 'Track changes is enabled; no edits made.' }

$snapshot = @(Get-Content -LiteralPath 'E:\PY\TTC\.presentation-review\cross-chain-fix\live-before.json' -Raw | ConvertFrom-Json)
$start = $snapshot | Where-Object {$_.Text -match '^Slide 14\b'}
$next = $snapshot | Where-Object {$_.Text -match '^Slide 15\b'}
$expected = @($snapshot | Where-Object {$_.Index -ge $start.Index -and $_.Index -lt $next.Index})
if ($expected.Count -ne 8) { throw 'Slide 14 paragraph structure changed; reload before editing.' }
foreach ($p in $expected) {
    if ($document.Paragraphs.Item($p.Index).Range.Text.TrimEnd([char]13,[char]7) -ne $p.Text) { throw 'Slide 14 changed after reading; no edits made.' }
}
$before = @()
for ($i=1; $i -le $document.Paragraphs.Count; $i++) { $before += $document.Paragraphs.Item($i).Range.Text }

$oldSelectionText = 'Solid lines use weighted best-of-N, while dashed lines use majority voting.'
$newSelectionText = 'For solid lines, the ORM selects within each chain and then across chains. For dashed lines, all answers from all chains vote together.'
$slide15First = $next.Index + 1
$slide15Text = $document.Paragraphs.Item($slide15First).Range.Text.TrimEnd([char]13,[char]7)
if (-not $slide15Text.Contains($oldSelectionText)) { throw 'Slide 15 wording changed; reload before editing.' }
$texts = @(
    'Slide 14 The Best Mix Depends on Difficulty and Budget',
    'Now we combine independent starts with sequential revisions. The example below uses 128 answers: eight chains, with sixteen complete answers in each chain.',
    'The ORM first makes a weighted choice inside each chain. It sums scores for matching final answers, then keeps the highest-scoring solution for the winning answer. We now have eight representatives. A second weighted choice across these eight gives one final answer.',
    'Both figures use this same selection process. In the left figure, each line keeps the total budget fixed. The horizontal axis is chain length divided by chain count. Our example has ratio two. At high budgets, a mix can beat both extremes.',
    'The right figure fixes the total budget at 128. Each group is a difficulty level, and the colors show different ratios. Easy questions favor longer chains. Harder questions often need more independent starts.',
    'Conclusions shown on the slide',
    'At high budgets, a mix can beat both extremes.',
    'Easy questions favor longer chains; harder ones often need more starts.'
)
$wordInstance.UndoRecord.StartCustomRecord('Explain cross-chain selection')
try {
    $p = $document.Paragraphs.Item($slide15First)
    $range = $document.Range($p.Range.Start,$p.Range.End-1)
    $range.Text = $slide15Text.Replace($oldSelectionText,$newSelectionText)
    for ($j=7; $j -ge 1; $j--) {
        $p = $document.Paragraphs.Item($start.Index+$j)
        $range = $document.Range($p.Range.Start,$p.Range.End-1)
        $range.Text = $texts[$j]
        $range.Font.Bold = $(if ($j -eq 5) {-1} else {0})
    }
} finally { $wordInstance.UndoRecord.EndCustomRecord() }

$allowed = @($expected | Select-Object -ExpandProperty Index) + @($slide15First)
if ($document.Paragraphs.Count -ne $before.Count) { throw 'Unexpected paragraph count change; inspect before saving.' }
for ($i=1; $i -le $document.Paragraphs.Count; $i++) {
    if ($i -notin $allowed -and $document.Paragraphs.Item($i).Range.Text -ne $before[$i-1]) { throw "Unexpected change outside selected sections at paragraph $i." }
}
$document.Save()
$document.ExportAsFixedFormat('E:\PY\TTC\.presentation-review\main-word.pdf',17)
[PSCustomObject]@{Saved=$document.Saved;Updated='Slide 14 and one selection-rule sentence in Slide 15';OtherTextPreserved=$true} | ConvertTo-Json -Compress
