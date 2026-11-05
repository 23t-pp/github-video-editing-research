from scout import *
import numpy as np
QA=ROOT/'outputs/jjk-edge-v17/evidence/原生选镜验收'
p=ROOT/'outputs/jjk-edge-v17/hyperframes/assets/shots/C07.mp4'
fs=[12,24,36,47]
r=subprocess.run([FF,'-v','error','-threads','1','-filter_threads','1','-i',str(p),'-vf',"select='eq(n,12)+eq(n,24)+eq(n,36)+eq(n,47)'",'-fps_mode','passthrough','-frames:v','4','-threads','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True);r.check_returncode()
a=np.frombuffer(r.stdout,np.uint8).reshape(4,1080,1920,3)
for f,arr in zip(fs,a):Image.fromarray(arr).save(QA/f'C07-lens-F{f:02}-1920.jpg',quality=95)
