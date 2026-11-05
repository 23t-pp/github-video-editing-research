from pathlib import Path
import sys,json,string
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'work/jjk-edge-v17/font-deps'))
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options
HF=BASE/'outputs/jjk-edge-v17-v2/hyperframes'
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
chars=string.printable+plan['title']+'五条悟夏油杰咒术回战记忆现实'
for event in plan['typeEvents']:
    for key in ['text','subtitle']:
        v=event.get(key,'');chars+=''.join(v) if isinstance(v,list) else v
font=TTFont('C:/Windows/Fonts/msyhbd.ttc',fontNumber=0)
options=Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
sub=Subsetter(options=options);sub.populate(text=chars);sub.subset(font)
font.save(HF/'assets/fonts/heavy.ttf')
print('V2 font subset', (HF/'assets/fonts/heavy.ttf').stat().st_size)
