import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {work,output,read,save,httpEntry} from './client.mjs';
const baseline=read(path.join(work,'准备状态.json'));
const label=process.argv[2]||'current';assert(/^[a-zA-Z0-9_-]+$/.test(label));
const checks=[];
for(const expected of baseline.protectedV1Projects){const e=await httpEntry('project:'+expected.projectId);assert(e.found);const actual=crypto.createHash('sha256').update(JSON.stringify(e.value)).digest('hex');checks.push({projectId:expected.projectId,baselineSha256:expected.docSha256,actualSha256:actual,equal:actual===expected.docSha256});}
const report={label,checks,v1ProjectsUnchanged:checks.every(c=>c.equal),writesToV1:0,verifiedAt:new Date().toISOString()};save(path.join(output,`${label}-V1保护核验.json`),report);assert(report.v1ProjectsUnchanged,'V1 document changed since V2 preparation');console.log(JSON.stringify(report));
