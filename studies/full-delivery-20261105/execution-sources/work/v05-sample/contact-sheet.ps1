param([string]$InputDir,[string]$OutputFile)
Add-Type -AssemblyName System.Drawing
$items=Get-Content -LiteralPath (Join-Path $InputDir 'latest.json') -Raw -Encoding UTF8|ConvertFrom-Json
$columns=5
$tileW=384
$tileH=184
$rows=[int][Math]::Ceiling($items.Count/$columns)
$bitmap=[System.Drawing.Bitmap]::new($columns*$tileW,$rows*$tileH)
$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
$graphics.Clear([System.Drawing.Color]::Black)
$font=[System.Drawing.Font]::new('Consolas',13)
for($i=0;$i -lt $items.Count;$i++){
 $x=($i%$columns)*$tileW
 $y=[int][Math]::Floor($i/$columns)*$tileH
 $img=[System.Drawing.Image]::FromFile((Join-Path $InputDir $items[$i].file))
 $graphics.DrawImage($img,$x,$y,$tileW,160)
 $label=([TimeSpan]::FromSeconds($items[$i].t)).ToString('hh\:mm\:ss')+'  '+$items[$i].t+'s'
 $graphics.DrawString($label,$font,[System.Drawing.Brushes]::White,$x+5,$y+160)
 $img.Dispose()
}
$bitmap.Save($OutputFile,[System.Drawing.Imaging.ImageFormat]::Jpeg)
$font.Dispose(); $graphics.Dispose(); $bitmap.Dispose()
Write-Output $OutputFile
