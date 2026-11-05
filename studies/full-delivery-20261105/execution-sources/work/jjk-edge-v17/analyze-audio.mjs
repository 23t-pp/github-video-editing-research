import fs from 'node:fs/promises';
import {analyze} from 'file:///C:/Users/PC/.codex/skills/montage/assets/dsh-montage/lib/analyze.js';
const root='D:/gpt/2026-11-04/ps-c-windows-system32-winget-install-2/outputs/jjk-edge-v17';
await fs.mkdir(root+'/hyperframes/audio-report',{recursive:true});
const r=await analyze({audio:'C:/Users/PC/Desktop/edge.mp3',window:60});
await fs.writeFile(root+'/hyperframes/audio-report/full-track-analysis.json',JSON.stringify(r,null,2));
console.log(JSON.stringify({candidates:r.candidates,bpmEstimate:r.bpm,energy139to212:r.waveform.slice(130).map((db,i)=>({s:130+i,db}))}));
