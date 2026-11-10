$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    foreach ($part in @('main','backup')) {
        $path = 'E:\PY\TTC\presentation\presentation paper\test-time-compute-' + $part + '-script.docx'
        $output = 'E:\PY\TTC\.presentation-review\conclusion-refresh\' + $part + '-word.pdf'
        $document = $word.Documents.Open($path,$false,$true)
        $document.ExportAsFixedFormat($output,17)
        $document.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
        $document = $null
        Write-Output ($part + ' script rendered.')
    }
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word -and $word.Documents.Count -eq 0) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
