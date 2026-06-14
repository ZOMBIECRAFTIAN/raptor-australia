param(
    [string]$InputDocx = "",
    [string]$OutputPdf = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($InputDocx)) {
    $InputDocx = Join-Path $projectRoot "docs\Australian_Raptor_Thesis_v1_5.docx"
}
if ([string]::IsNullOrWhiteSpace($OutputPdf)) {
    $OutputPdf = Join-Path $projectRoot "docs\Australian_Raptor_Thesis_v1_5.pdf"
}

$docxPath = (Resolve-Path $InputDocx).Path
$pdfPath = [System.IO.Path]::GetFullPath($OutputPdf)

$word = $null
$doc = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0

    $doc = $word.Documents.Open($docxPath, $false, $true)

    foreach ($field in $doc.Fields) {
        try {
            $null = $field.Update()
        } catch {
            # Some generated fields may not be updateable in read-only mode.
        }
    }

    # 17 is wdExportFormatPDF.
    $doc.ExportAsFixedFormat($pdfPath, 17)
    Write-Output $pdfPath
} finally {
    if ($null -ne $doc) {
        $doc.Close($false)
        $null = [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
    }
    if ($null -ne $word) {
        $word.Quit()
        $null = [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
