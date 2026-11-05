from pathlib import Path
import sys,json,string
W=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'font-deps'))
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter,Options
HF=W.parents[1]/'outputs/jjk-edge-v17/hyperframes'
plan=json.loads((HF/'edit.json').read_text(encoding='utf-8'))
chars=string.printable+'五条悟夏油杰咒术回战'
for event in plan['typeEvents']:
    value=event['text'];chars+=''.join(value) if isinstance(value,list) else value
font=TTFont('C:/Windows/Fonts/msyhbd.ttc',fontNumber=0)
options=Options();options.name_IDs=['*'];options.name_legacy=True;options.name_languages=['*']
sub=Subsetter(options=options);sub.populate(text=chars);sub.subset(font)
font.save(HF/'assets/fonts/heavy.ttf')
print('Subset saved', (HF/'assets/fonts/heavy.ttf').stat().st_size)
