Add-Type -AssemblyName System.Drawing
$dir=Join-Path (Get-Location) 'outputs\reference-library-20261105\fastx-120\evidence'
$items=Get-Content -LiteralPath (Join-Path $dir 'scout-index.json') -Raw -Encoding UTF8|ConvertFrom-Json
$bitmap=[System.Drawing.Bitmap]::new(1920,1104)
$g=[System.Drawing.Graphics]::FromImage($bitmap)
$g.Clear([System.Drawing.Color]::Black)
$font=[System.Drawing.Font]::new('Consolas',13)
for($i=0;$i -lt $items.Count;$i++){$x=($i%5)*384;$y=[int][Math]::Floor($i/5)*184;$img=[System.Drawing.Image]::FromFile((Join-Path $dir $items[$i].file));$g.DrawImage($img,$x,$y,384,160);$g.DrawString(([TimeSpan]::FromSeconds($items[$i].t)).ToString('hh\:mm\:ss')+'  '+$items[$i].t+'s',$font,[System.Drawing.Brushes]::White,$x+5,$y+162);$img.Dispose()}
$bitmap.Save((Join-Path $dir '速激素材候选总览.jpg'),[System.Drawing.Imaging.ImageFormat]::Jpeg)
$font.Dispose();$g.Dispose();$bitmap.Dispose()
