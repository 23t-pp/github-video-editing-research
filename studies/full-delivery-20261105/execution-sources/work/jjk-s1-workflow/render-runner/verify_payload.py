"""Verify current-plan chunks; optional producer-only rebind requires exact pixel-input closure."""
from pathlib import Path
import argparse,json,hashlib,sys,tempfile,shutil,time
BASE=Path(__file__).resolve().parents[3];ROOT=BASE/'outputs/jjk-s1-workflow';HF=ROOT/'hyperframes';sys.path.insert(0,str(HF));import render
p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--chunks',type=int,nargs='+',default=list(range(20)));p.add_argument('--report',type=Path,required=True);p.add_argument('--allow-producer-rebind',action='store_true');a=p.parse_args()
plan_path=a.plan.resolve();plan=json.loads(plan_path.read_text(encoding='utf-8'));work=a.work.resolve();assert work.is_relative_to(BASE),'temporary proof work must remain inside workspace';runtime=render.runtime_fingerprint();assets={x['id']:x for x in plan['assets']};rows=[]
def producer(name):return name.endswith('.py') or name=='barlow-glyphs.json'
def pixel_spec(s):return {**s,'dependencies':{k:v for k,v in s['dependencies'].items() if not producer(k)}}
for chunk in a.chunks:
 first=chunk*72;last=min(first+72,plan['durationFrames']);html,needed,copies,key,spec=render.make_chunk(plan,first,last,runtime);folder=work/f'chunk-{chunk:02}';file=folder/'render-proof.json';proof=json.loads(file.read_text(encoding='utf-8'));movie=ROOT/'occ-effects'/f'HF-{first:04}-{last:04}.mp4'
 if render.cache_valid(folder,key,work/'master-frames',first,last,movie):
  rows.append({'chunk':chunk,'state':'current_key_and_all_payload_hashes_match','key':key,'actualPayloadSha256':proof['actualPayloadSha256']});continue
 assert a.allow_producer_rebind,('chunk not current',chunk)
 old_key=proof['renderKey'];assert render.cache_valid(folder,old_key,work/'master-frames',first,last,movie),('stored capture changed',chunk)
 assert pixel_spec(proof['inputSpec'])==pixel_spec(spec),('actual HTML/assets/runtime changed; must recapture',chunk)
 # Verify actual copied browser inputs against current root bytes, not only metadata hashes.
 actual_frames={Path(k).name:v for k,v in proof['actualRenderPayloadFiles'].items() if '/assets/frames/' in k.replace('\\','/')}
 assert set(actual_frames)=={f'{aid}-{n:04}.png' for aid,n in needed},('needed source frames changed',chunk)
 for name in ['hyperframes.json','assets/gsap.min.js',*copies,*[x.relative_to(HF).as_posix() for x in (HF/'assets/fonts').glob('*')]]:
  matches=[v for k,v in proof['actualRenderPayloadFiles'].items() if k.replace('\\','/').endswith('/'+name)]
  assert len(matches)==1 and matches[0]==render.sha(HF/name),('copied browser dependency changed',chunk,name)
 # Re-decode current source through the same extraction path and compare every RGB PNG byte hash.
 with tempfile.TemporaryDirectory(prefix='payload-check-',dir=work) as tmp:
  temp=Path(tmp);assert temp.resolve().is_relative_to(work.resolve())
  for aid in sorted({aid for aid,n in needed}):render.extract(assets[aid],{n for v,n in needed if v==aid},temp)
  for name,digest in actual_frames.items():assert render.sha(temp/name)==digest,('real source RGB PNG changed',chunk,name)
 history=folder/'proof-history';history.mkdir(exist_ok=True);previous=history/f'{old_key[:16]}-{int(time.time())}.json';shutil.copy2(file,previous)
 changes={k:{'old':proof['inputSpec']['dependencies'].get(k),'new':spec['dependencies'].get(k)} for k in sorted(set(proof['inputSpec']['dependencies'])|set(spec['dependencies'])) if proof['inputSpec']['dependencies'].get(k)!=spec['dependencies'].get(k)}
 assert all(producer(k) for k in changes),('nonproducer dependencies changed',changes)
 proof.setdefault('reuseHistory',[]).append({'oldRenderKey':old_key,'oldInputSpec':proof['inputSpec'],'newValidationPlanSha256':render.sha(plan_path),'changedProducerFiles':changes,'actualPixelInputsByteEqual':True,'allSourcePngReDecodedAndShaMatched':len(actual_frames),'preservedPreviousProof':previous.relative_to(folder).as_posix(),'validatedAtUnix':time.time(),'validator':'/root/s1_render_execution'})
 proof.update(renderKey=key,inputSpec=spec,currentValidationPlanSha256=render.sha(plan_path));render.write_json(file,proof)
 assert render.cache_valid(folder,key,work/'master-frames',first,last,movie)
 rows.append({'chunk':chunk,'state':'producer_changed_but_actual_pixel_inputs_byte_equal_reused','key':key,'actualPayloadSha256':proof['actualPayloadSha256'],'realSourcePngReDecoded':len(actual_frames),'changes':changes})
report={'state':'pass_input_consistency_only','plan':str(plan_path),'planSha256':render.sha(plan_path),'chunks':rows,'frames':sum(min((r['chunk']+1)*72,plan['durationFrames'])-r['chunk']*72 for r in rows),'scope':'Exact generated HTML, runtime/capture flags, source media bytes and real re-decoded source RGB PNGs,alpha,font,GSAP/config,output PNG/segment SHA; no artistic approval. Producer-only rebind never changes captured files.'};render.write_json(a.report,report);print(json.dumps({'state':report['state'],'chunks':len(rows),'frames':report['frames'],'rebound':sum(x['state'].startswith('producer_changed') for x in rows)},ensure_ascii=False))
