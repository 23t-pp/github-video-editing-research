from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent
probe='C:/Users/PC/Apps/ffmpeg/bin/ffprobe.exe'
items={}
for file in sorted(Path('D:/速度与激情').iterdir()):
    if file.suffix.lower() not in {'.mp4','.mkv','.mov'}: continue
    raw=subprocess.check_output([probe,'-v','error','-show_entries','stream=index,codec_type,codec_name,width,height,avg_frame_rate,color_space,color_transfer,color_primaries,color_range,channels,channel_layout:stream_tags=language,title:format=duration','-of','json',str(file)])
    report=json.loads(raw); video=next(s for s in report['streams'] if s['codec_type']=='video'); audio=[s for s in report['streams'] if s['codec_type']=='audio']
    film=file.name[:2];items[film]={'film':film,'file':str(file),'name':file.name,'seconds':float(report['format']['duration']),'video':video,'audio':audio};print(film,video['width'],video['height'],video['avg_frame_rate'],video.get('color_transfer'),[(s.get('index'),s.get('channel_layout'),s.get('tags',{}).get('language')) for s in audio])
(root/'inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
