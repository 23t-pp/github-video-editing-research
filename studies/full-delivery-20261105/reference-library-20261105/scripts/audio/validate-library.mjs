import fs from 'node:fs';import path from 'node:path';import os from 'node:os';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
const project=path.resolve(import.meta.dirname,'../..'),data=path.join(project,'data/audio');
const ff=process.env.FFMPEG_PATH||path.join(os.homedir(),'Apps/ffmpeg/bin/ffmpeg.exe');
const read=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
const index=read(path.join(data,'music-index.json')),checks=[],issues=[];
if(index.length!==20||new Set(index.map(r=>r.id)).size!==20)issues.push('Expected 20 unique video IDs');
for(const row of index){for(const [kind,relative,record] of [['mixed',row.mix_path,row.mix],['music-candidate',row.no_vocals_candidate_path,row.candidate]]){
 const issue=[];if(!relative||!record){issues.push(`${row.id}/${kind}: not complete`);continue}
 if(!relative.startsWith('audio/')||relative.includes('..')||path.isAbsolute(relative)){issues.push(`${row.id}/${kind}: invalid public path`);continue}
 const file=path.join(project,relative);if(!fs.existsSync(file)){issues.push(`${row.id}/${kind}: missing file`);continue}
 const buf=fs.readFileSync(file),sha=crypto.createHash('sha256').update(buf).digest('hex');
 if(sha!==record.sha256)issue.push('SHA256 mismatch');if(buf.length!==record.bytes)issue.push('byte length mismatch');
 const result=spawnSync(ff,['-nostdin','-v','error','-xerror','-i',file,'-map','0:a:0','-f','null','-'],{windowsHide:true,maxBuffer:4*1024*1024,timeout:120000});
 if(result.status!==0)issue.push('Full decode failed');
 if(kind==='music-candidate'&&!Number.isFinite(record.loudness?.integrated_lufs))issue.push('Non-finite loudness / possibly silent output');
 if(kind==='music-candidate'&&Math.abs(record.duration_sec-row.mix.source_decoded_duration_sec)>.15)issue.push('Duration differs by over 150ms');
 checks.push({id:row.id,kind,file:relative,sha256_verified:sha===record.sha256,bytes_verified:buf.length===record.bytes,full_decode_exit_code:result.status,duration_sec:record.duration_sec,passed:issue.length===0,issues:issue});
 issues.push(...issue.map(x=>`${row.id}/${kind}: ${x}`));
}}
function scan(value,where){if(typeof value==='string'&&(/^[A-Za-z]:[\\/]/.test(value)||value.includes('\\Users\\')||value.includes('/Users/')))issues.push(`Absolute local path in public JSON: ${where}`);else if(value&&typeof value==='object')for(const [key,item]of Object.entries(value))scan(item,where+'.'+key)}
for(const file of fs.readdirSync(data).filter(f=>f.endsWith('.json')))scan(read(path.join(data,file)),file);
const result={validated_at:new Date().toISOString(),passed:issues.length===0,files_checked:checks.length,mixed_checked:checks.filter(c=>c.kind==='mixed').length,candidates_checked:checks.filter(c=>c.kind==='music-candidate').length,claims_not_tested:['Listening quality','Removal of all vocals/dialogue/SFX','Song identification','Music licensing ownership'],checks,issues};
fs.writeFileSync(path.join(data,'validation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({passed:result.passed,files_checked:checks.length,issues}));if(issues.length)process.exitCode=1;
