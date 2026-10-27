$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$presentation = $ppt.Presentations.Open('e:\IoT\DoAn\docs\pptx\Bao_Cao_He_Thong_IoT_4_Slides_Nhom04_Chuan.pptx', [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
$outputDir = 'e:\IoT\DoAn\docs\pptx\slides_export'
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

for ($i = 1; $i -le $presentation.Slides.Count; $i++) {
    $slide = $presentation.Slides.Item($i)
    $exportPath = Join-Path $outputDir ("slide_{0:D2}.png" -f $i)
    $slide.Export($exportPath, 'PNG', 1920, 1080)
    Write-Host "Exported Slide $i to $exportPath"
}

$presentation.Close()
$ppt.Quit()
Write-Host "Export completed successfully!"
