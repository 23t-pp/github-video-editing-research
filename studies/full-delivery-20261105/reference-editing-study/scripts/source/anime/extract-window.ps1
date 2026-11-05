param(
 [Parameter(Mandatory=$true)][ValidateSet('V02','V03','V05','V07')][string]$Id,
 [Parameter(Mandatory=$true)][double]$Start,
 [int]$Rate=10,
 [int]$Columns=5,
 [int]$Rows=4,
 [string]$Label='detail'
)
$ErrorActionPreference='Stop'
$base=Split-Path -Parent $PSCommandPath
$manifest=Get-Content -LiteralPath (Join-Path (Split-Path -Parent $base) 'manifest.local.json') -Raw|ConvertFrom-Json
$video=$manifest|Where-Object{$_.id -eq $Id}
$fmt=[Globalization.CultureInfo]::InvariantCulture
$startText=$Start.ToString('0.000',$fmt)
$duration=($Columns*$Rows/$Rate).ToString('0.000',$fmt)
$out=Join-Path $base "$Id-$Label-$startText.jpg"
$filter="fps=$Rate,scale=320:180,setpts=PTS+$startText/TB,drawtext=fontfile='C\:/Windows/Fonts/consola.ttf':text='%{pts\:hms}':x=5:y=5:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.8,tile=${Columns}x${Rows}"
$psi=[Diagnostics.ProcessStartInfo]::new()
$psi.FileName='C:\Users\PC\Apps\ffmpeg\bin\ffmpeg.exe'
$psi.UseShellExecute=$false
$psi.CreateNoWindow=$true
$psi.RedirectStandardOutput=$true
$psi.RedirectStandardError=$true
foreach($arg in @('-hide_banner','-loglevel','error','-nostdin','-ss',$startText,'-i',$video.path,'-t',$duration,'-vf',$filter,'-frames:v','1','-q:v','2','-f','image2pipe','-vcodec','mjpeg','pipe:1')){$psi.ArgumentList.Add($arg)}
$process=[Diagnostics.Process]::Start($psi)
$stderrTask=$process.StandardError.ReadToEndAsync()
$fileStream=[IO.File]::Create($out)
try{$process.StandardOutput.BaseStream.CopyTo($fileStream)}finally{$fileStream.Dispose()}
$process.WaitForExit()
$stderr=$stderrTask.Result
if($process.ExitCode -ne 0){throw "ffmpeg failed: $($process.ExitCode) $stderr"}
[pscustomobject]@{id=$Id;start=$Start;duration=[double]$duration;rate=$Rate;columns=$Columns;rows=$Rows;file=$out;source_sha256=$video.sha256}|ConvertTo-Json|Set-Content -LiteralPath "$out.json" -Encoding utf8
Write-Output $out
