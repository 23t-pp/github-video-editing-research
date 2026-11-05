import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import{spawnSync}from'node:child_process';import assert from'node:assert/strict';
const gh='C:/Program Files/GitHub CLI/gh.exe',repo='23t-pp/github-video-editing-research',tag='reference-library-2026-11-05',commit='ab529b1c023e8c6b7d01a464229403d6dd0e1cf2',out=path.resolve('outputs/reference-library-release-20261105');
function cli(args){const p=spawnSync(gh,args,{encoding:'utf8',windowsHide:true,maxBuffer:4*1024*1024});if(p.status!==0)throw Error(p.stderr);return p.stdout;}
const fields='tagName,isDraft,targetCommitish,url,assets';
let r=JSON.parse(cli(['release','view',tag,'--repo',repo,'--json',fields]));assert.equal(r.targetCommitish,commit);assert.equal(r.assets.length,3);
const verified=r.assets.map(a=>{const p=path.join(out,a.name),b=fs.readFileSync(p),sha=crypto.createHash('sha256').update(b).digest('hex');assert.equal(a.size,b.length);assert.equal(a.digest,'sha256:'+sha);assert.equal(a.state,'uploaded');return {name:a.name,bytes:a.size,sha256:sha,githubDigestMatches:true};});
if(r.isDraft)cli(['release','edit',tag,'--repo',repo,'--draft=false']);
r=JSON.parse(cli(['release','view',tag,'--repo',repo,'--json',fields]));assert.equal(r.isDraft,false);assert.equal(r.tagName,tag);assert.ok(r.url.endsWith('/'+tag));
const api=await fetch(`https://api.github.com/repos/${repo}/releases/tags/${tag}`,{headers:{'User-Agent':'video-editing-study-verification'}});assert.equal(api.status,200);const publicRelease=await api.json();assert.equal(publicRelease.draft,false);assert.equal(publicRelease.assets.length,3);
for(const a of publicRelease.assets){const head=await fetch(a.browser_download_url,{method:'HEAD'});assert.equal(head.status,200);assert.equal(Number(head.headers.get('content-length')),a.size);}
const receipt={date:new Date().toISOString(),repository:'https://github.com/'+repo,publicRepository:true,commit,commitUrl:`https://github.com/${repo}/commit/${commit}`,releaseUrl:r.url,tag,publicReleaseVerifiedWithoutAuthentication:true,assets:verified.map(a=>({...a,url:r.assets.find(b=>b.name===a.name).url})),scope:'中文报告、脚本、证据和源码在main；音频和可编辑媒体包在Release。未上传整部原片、私有路径配置或模型权重。'};
fs.writeFileSync(path.join(out,'发布验证.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify(receipt,null,2));
