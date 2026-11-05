"""Generate the editable HyperFrames HTML and frame-accurate effects render views."""
from html import escape
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parent
STYLE = (ROOT / 'style.css')


def load_edit():
    return json.loads((ROOT / 'edit.json').read_text(encoding='utf-8-sig'))


def save_editable(document):
    target=ROOT/'index.html'
    signature=ROOT/'generated-index.sha256'
    content=document.encode('utf-8')
    if target.is_file() and target.read_bytes()!=content and signature.is_file():
        old=target.read_bytes()
        actual=hashlib.sha256(old).hexdigest()
        if actual!=signature.read_text().strip():
            backup=ROOT/f'index-studio-{actual[:12]}.html'
            if not backup.exists():
                backup.write_bytes(old)
            print(f'Studio edits preserved in {backup.name}. This render uses edit.json, style.css and composition.py.',flush=True)
    target.write_bytes(content)
    signature.write_text(hashlib.sha256(content).hexdigest()+'\n', encoding='ascii')


def build(plan, first=0, last=None, frame_mode=False):
    fps = plan['fps']
    last = plan['durationFrames'] if last is None else last
    seconds = lambda frames: f'{frames / fps:.9f}'
    title = plan['effects']['title']
    trip = plan['effects']['triptych']
    fade = plan['effects']['endFade']
    assets = {asset['id']: asset for asset in plan['assets']}
    needed = set()
    animation = []

    def overlaps(start, end):
        return first < end and last > start

    def media(tag, asset, start, end, track):
        a, b = max(start, first), min(end, last)
        if a >= b:
            return ''
        if frame_mode:
            items = []
            for frame in range(a, b):
                index = asset['assetStartFrame'] + frame - start
                key = (asset['id'], index)
                needed.add(key)
                uri = f'assets/frames/{key[0]}-{key[1]:03}.png'
                items.append(f'<img id="{tag}-{frame}" class="clip source" src="{uri}" alt="" data-start="{seconds(frame-first)}" data-duration="{seconds(1)}" data-track-index="{track}" data-layout-allow-overlap="true">')
            return '\n'.join(items)
        offset = asset['assetStartFrame'] + a - start
        uri = escape(asset['asset'], quote=True)
        return f'<video id="{tag}" class="clip source" src="{uri}" muted playsinline preload="metadata" data-start="{seconds(a-first)}" data-duration="{seconds(b-a)}" data-media-start="{seconds(offset)}" data-track-index="{track}" data-volume="0" data-layout-allow-overlap="true"></video>'

    base = '\n'.join(media('base-'+s['id'], assets[s['id']], s['startFrame'], s['startFrame']+s['frames'], 0) for s in plan['shots'])
    layers = [f'<div class="plane" id="footage">{base}</div>']
    if overlaps(title['startFrame'], title['endFrame']):
        a, b = title['startFrame'], title['endFrame']
        layers.append(f'''<div id="titles" class="title-layer" data-layout-allow-overlap="true"><div class="lockup"><div class="word-mask"><div class="word">{escape(title["text"])}</div></div><div class="signature"><span class="stroke"></span><span class="latin">{escape(title["latin"])}</span></div></div></div>''')
        animation += [
            f"tl.set('#titles',{{visibility:'visible'}},{seconds(a-first)});",
            f"tl.fromTo('.word',{{y:112,skewY:5}},{{y:0,skewY:0,duration:{seconds(12)},ease:'power3.out'}},{seconds(a-first)});",
            f"tl.fromTo('.signature',{{opacity:0,x:-24}},{{opacity:1,x:0,duration:{seconds(10)},ease:'power2.out'}},{seconds(a+4-first)});",
            f"tl.to('.lockup',{{opacity:0,x:14,duration:{seconds(9)},ease:'power2.in'}},{seconds(b-9-first)});",
            f"tl.set('#titles',{{visibility:'hidden'}},{seconds(b-first)});"
        ]
    if overlaps(trip['startFrame'], trip['endFrame']):
        panels = []
        for i, spec in enumerate(trip['panels']):
            x0 = [0,642,1282][i]
            width = [638,636,638][i]
            start = trip['startFrame'] + spec['delay']
            offset = round(width/2-spec['focusX']*plan['width'])
            play = media(f'look-{i}',assets[spec['assetId']], start,trip['endFrame'],i+1)
            panels.append(f'<div id="panel-{i}" class="panel" style="left:{x0}px;width:{width}px"><div class="panel-source" style="left:{offset}px">{play}</div></div>')
            animation.append(f"tl.fromTo('#panel-{i}',{{opacity:0,x:{[18,0,-18][i]}}},{{opacity:1,x:0,duration:{seconds(3)},ease:'power2.out'}},{seconds(start-first)});")
        layers.append('<div class="panels" id="panels" data-layout-allow-overlap="true">' + ''.join(panels) + '</div>')
        animation += [
            f"tl.set('#panels',{{visibility:'visible'}},{seconds(trip['startFrame']-first)});",
            f"tl.set('#panels',{{visibility:'hidden'}},{seconds(trip['endFrame']-first)});"
        ]
    if overlaps(fade['startFrame'], fade['endFrame']):
        layers.append('<div id="fade" class="fade"></div>')
        animation.append(f"tl.fromTo('#fade',{{opacity:0}},{{opacity:1,duration:{seconds(fade['endFrame']-fade['startFrame']-1)},ease:'power1.inOut'}},{seconds(fade['startFrame']-first)});")
    if not frame_mode:
        layers.append(f'<audio id="master-audio" src="{escape(plan["audio"]["master"],quote=True)}" data-start="0" data-duration="{seconds(last-first)}" data-track-index="6" data-volume="1"></audio>')
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><title>{escape(plan['title'])}</title>
<script src="assets/gsap.min.js"></script><style>{STYLE.read_text(encoding='utf-8')}</style></head><body>
<main id="root" data-composition-id="apex" data-start="0" data-duration="{seconds(last-first)}" data-width="{plan['width']}" data-height="{plan['height']}" data-fps="{fps}" data-layout-allow-overlap="true">
{chr(10).join(layers)}
</main><script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});{chr(10).join(animation)}
window.__timelines.apex=tl;</script></body></html>'''
    return html, needed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rebuild the editable HyperFrames composition from edit.json.')
    parser.parse_args()
    document, _ = build(load_edit())
    save_editable(document)
    print('HyperFrames index.html rebuilt')
