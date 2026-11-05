from final_candidates import *
def strip(ep,start,dur,label,fps=4):
 r=subprocess.run([FF,'-v','error','-ss',str(start),'-i',str(base/f'{ep:02}.mp4'),'-t',str(dur),'-vf',f'fps={fps},scale=384:216','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True);r.check_returncode()
 n=len(r.stdout)//(384*216*3);arr=np.frombuffer(r.stdout,dtype=np.uint8)[:n*384*216*3].reshape(n,216,384,3)
 canvas=Image.new('RGB',(1536,242*((n+3)//4)),(15,15,15));d=ImageDraw.Draw(canvas)
 for k,frame_ in enumerate(arr):
  x=k%4*384;y=k//4*242;canvas.paste(Image.fromarray(frame_),(x,y));d.text((x+4,y+217),f'e{ep:02} {start+k/fps:.3f}s',font=font,fill='white')
 canvas.save(OUT/f'{label}.jpg',quality=88)
 print(label,flush=True)
if __name__=='__main__':
 for args in [(4,785,10,'hurt-785-795',2),(2,1259,9,'glass-1259-1268',4),(3,878.5,3,'blue-878-881',8),(3,888.5,3,'blue-888-891',8),(4,429,2,'geto-429-431',8),(4,449,2,'geto-449-451',8),(4,1338,4,'hurt-1338-1342',4)]:strip(*args)
