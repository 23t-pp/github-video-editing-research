from pathlib import Path
from PIL import Image
import subprocess,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];FF='C:/Users/PC/Apps/ffmpeg/bin/ffmpeg.exe';C=R/'loops/loop-02/review-pilot-inputs/alpha'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((C/'XCHASE-final-manifest.json').read_text(encoding='utf-8'))
assert all(sha(R/x['path'])==x['sha256'] for x in manifest['files'])
result=[]
for g in ['XCHASE','XPALM']:
    rep=json.loads((C/f'{g}-alpha-report.json').read_text(encoding='utf-8'));movie=R/rep['preparedMovie'];assert sha(movie)==rep['preparedSha256']
    raw=subprocess.run([FF,'-v','error','-threads','1','-i',str(movie),'-an','-vf','scale=in_color_matrix=bt709:in_range=tv:out_range=full,format=rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True).stdout
    frames=np.frombuffer(raw,dtype=np.uint8).reshape(-1,1080,1920,3)
    checks=[]
    for n in range(2,28):
        p=R/f'hyperframes/assets/alpha/{g}/{n:06}.png';im=Image.open(p);assert im.mode=='RGBA';arr=np.array(im)
        assert np.array_equal(arr[:,:,:3],frames[n]),(g,n,'RGB differs')
        assert not arr[:60,:,3].any() and not arr[1020:,:,3].any(),(g,n,'black band alpha nonzero')
        if g=='XCHASE':assert not arr[1008:,:,3].any()
        checks.append({'frame':n,'path':p.relative_to(R).as_posix(),'sha256':sha(p),'allRgbExact':True})
    result.append({'group':g,'framesChecked':26,'range':[2,28],'allRgbEqualsSamePreparedFrame':True,'blackBandsAlphaZero':True,'preparedMovieSha256':sha(movie),'pngChecks':checks})
(R/'loops/loop-02/review-alpha-machine.json').write_text(json.dumps({'reviewer':'/root/s1_design_auditor','status':'pass_material_rgb_integrity_only','XCHASEManifestSha256':sha(C/'XCHASE-final-manifest.json'),'frozenManifestAllFilesMatch':True,'groups':result,'scope':'All52 alpha PNG RGB pixels versus same prepared decoded frame and alpha blackbands; this does not approve contour accuracy or composition placement.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Independent alpha integrity pass:52 RGB matches; frozen manifest matches; no composition approval')
