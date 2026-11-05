from pathlib import Path
import shutil,json
R=Path(__file__).resolve().parent.parent;OLD=R.parent/'jjk-edge-v17-v2/hyperframes';H=R/'hyperframes'
H.mkdir(exist_ok=True)
# Code/font reuse only. No Season 2 picture, movie or alpha is copied.
for name in ['composition.py','typefx.py','barlow-glyphs.json','layoutfx.py','hf.mjs','hyperframes.json']:
    shutil.copy2(OLD/name,H/name)
for name in ['assets/gsap.min.js','assets/fonts/BarlowCondensed-ExtraBold.woff2']:
    dest=H/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/name,dest)
shutil.copy2('C:/Windows/Fonts/msyhbd.ttc',H/'assets/fonts/cjk-heavy.ttc')
(H/'DESIGN.md').write_text('''# 咒力接力 · CURSED FLOW

## Style Prompt
第一季角色动作接力，少量原创档案屏与漫画术式字；源冷绿、森林绿、黄昏橙、术式青紫按段落切换，避免全片一种滤镜。V20动作/焦点/停顿骨架，复杂遮挡按证据制作。

## Colors
- #080b13 背景/短停顿。
- #fff7de 温白信息与细高光。
- #bb1422 咒力红与短重击。
- #72c7ed 青掌与电弧。
- #b517c6 术式紫的挤出与裂口光。

## Typography
Barlow Condensed ExtraBold主英文，Microsoft YaHei Bold中文辅助。短信息、少量大字，不冒充歌词。

## Motion
24fps/1440帧。动作主体与源时钟优先；七叶同源、alpha同帧RGB；复杂效果分72帧离线渲染，不用实时随机数。

## What NOT to Do
不要复用第二季像素或alpha；不要用静态剪影冒充动态；不要把原术式称新CG；不要持续压字遮眼；不要把所有镜头均分小窗。
''',encoding='utf-8')
p=H/'composition.py';s=p.read_text(encoding='utf-8').replace('assets/fonts/heavy.ttf','assets/fonts/cjk-heavy.ttc')
s=s.replace("    layout_html,layout_css=layout_layers", "    from screenfx import screen_layers\n    screen_html,screen_css=screen_layers(plan,fps,first,last,media,setat)\n    layers.append(screen_html)\n    layout_html,layout_css=layout_layers")
s=s.replace("'''+css+layout_css", "'''+css+layout_css+screen_css")
s=s.replace("print('Generated V17 + V02 editable composition')", "print('Generated Season 1 CURSED FLOW editable composition')")
p.write_text(s,encoding='utf-8')
print('Copied code/fonts only; no S2 picture assets')
