Add-Type -AssemblyName System.Drawing
$dir=Join-Path $PSScriptRoot '..\..\outputs\v05-six-panel\evidence'
$items=Get-Content -LiteralPath (Join-Path $dir '关键帧索引.json') -Raw -Encoding UTF8|ConvertFrom-Json
$bitmap=[System.Drawing.Bitmap]::new(1600,1050)
$g=[System.Drawing.Graphics]::FromImage($bitmap)
$g.Clear([System.Drawing.Color]::FromArgb(12,16,20))
$font=[System.Drawing.Font]::new('Consolas',14)
for($i=0;$i -lt $items.Count;$i++){
 $x=($i%4)*400; $y=[int][Math]::Floor($i/4)*262
 $img=[System.Drawing.Image]::FromFile((Join-Path $dir $items[$i].file))
 $g.DrawImage($img,$x,$y,400,225)
 $label='Frame '+$items[$i].frame+'  |  '+([Math]::Round($items[$i].t,3))+' s'
 $g.DrawString($label,$font,[System.Drawing.Brushes]::White,$x+10,$y+230)
 $img.Dispose()
}
$bitmap.Save((Join-Path $dir '成片逐帧拆解.jpg'),[System.Drawing.Imaging.ImageFormat]::Jpeg)
$font.Dispose();$g.Dispose();$bitmap.Dispose()
