import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import vm from 'node:vm';
const root=path.resolve(import.meta.dirname,'../../outputs/reference-editing-study');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const manifest=read('data/manifest.json'),reviews=read('data/reviews.json');
assert.equal(manifest.length,10);assert.equal(reviews.length,10);
let segments=0,refs=0;const coverage=[];
for(const v of reviews){const m=manifest.find(x=>x.id===v.id);assert(m);let end=0;
 for(const s of v.segments){segments++;assert(s.start>=0&&s.end>s.start&&s.end<=m.duration+0.002,`${v.id} range`);assert(s.start<=end+0.002,`${v.id} gap ${end}-${s.start}`);end=Math.max(end,s.end);
  for(const p of s.evidence){refs++;assert(/^evidence\/V\d{2}\/[\w .-]+\.jpg$/i.test(p),p);assert(fs.existsSync(path.join(root,p)),p)}
 }assert(Math.abs(end-m.duration)<0.002);coverage.push({id:v.id,covered_to:end,segments:v.segments.length});assert(read(`data/audio/${v.id}.json`).id===v.id);
}
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');new vm.Script(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
const broken=[];for(const f of fs.readdirSync(root).filter(f=>f.endsWith('.md'))){const t=fs.readFileSync(path.join(root,f),'utf8');for(const m of t.matchAll(/\]\(([^)]+)\)/g)){let p=m[1].replace(/^<|>$/g,'');if(/^(?:https?:|#|[A-Za-z]:)/.test(p))continue;p=p.split('#')[0];if(p&&!fs.existsSync(path.join(root,p)))broken.push({doc:f,target:p});}}assert.deepEqual(broken,[]);
const base='http://127.0.0.1:5208';const health=await(await fetch(base+'/health')).json();assert.equal(health.media_count,10);
const checks=await Promise.all(manifest.map(async v=>{const r=await fetch(base+'/media/'+v.id,{headers:{Range:'bytes=0-127'}});assert.equal(r.status,206);assert.equal((await r.arrayBuffer()).byteLength,128);return {id:v.id,range_status:r.status,bytes:128}}));
const guards=[];for(const [url,status,headers] of [['/local-config.json',403],['/media/V99',404],['/media/V01',416,{Range:'bytes=999999999-'}]]){const r=await fetch(base+url,{headers});assert.equal(r.status,status);await r.text();guards.push({url,status})}
const evidenceImages=manifest.reduce((n,v)=>n+fs.readdirSync(path.join(root,'evidence',v.id)).filter(f=>f.endsWith('.jpg')).length,0);
const out={verified_at:new Date().toISOString(),videos:10,segments,evidence_links:refs,evidence_images:evidenceImages,coverage,html_js_syntax:'pass',markdown_local_links:'pass',http_health:health,http_range:checks,http_guards:guards,replica_rendered:false,audio_listened:false};
fs.writeFileSync(path.join(root,'data/verification.json'),JSON.stringify(out,null,2));
const counts=read('data/study-counts.json');counts.evidence_images=evidenceImages;fs.writeFileSync(path.join(root,'data/study-counts.json'),JSON.stringify(counts,null,2));
console.log(JSON.stringify({videos:10,segments,evidence_links:refs,evidence_images:evidenceImages,coverage:'pass',links:'pass',html_js:'pass',http:'pass'}));
