$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open('E:\PY\TTC\presentation\presentation paper\test-time-compute-backup-script.docx',$false,$true)
    $document.ExportAsFixedFormat('E:\PY\TTC\.presentation-review\remove-last-three\backup-word.pdf',17)
    $document.Close(0)
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    $document = $null
    Write-Output 'Updated backup script rendered.'
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word -and $word.Documents.Count -eq 0) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
