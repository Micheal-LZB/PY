$ErrorActionPreference = 'Stop'
$word = $null
$doc = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  foreach ($name in @('main', 'backup')) {
    $sourcePath = 'E:\PY\TTC\presentation\presentation paper\test-time-compute-' + $name + '-script.docx'
    $destinationPath = 'E:\PY\TTC\.presentation-review\' + $name + '-word.pdf'
    $doc = $word.Documents.Open($sourcePath, $false, $true)
    $doc.ExportAsFixedFormat($destinationPath, 17)
    $doc.Close(0)
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
    $doc = $null
    Write-Output $destinationPath
  }
} finally {
  if ($null -ne $doc) { $doc.Close(0) }
  if ($null -ne $word) {
    $word.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
  }
}
