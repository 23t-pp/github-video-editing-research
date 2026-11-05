import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
export const taskWork=import.meta.dirname;
export const workspace=path.resolve(taskWork,'../../..');
export const taskRoot=path.join(workspace,'outputs/jjk-s1-workflow');
export const taskOutput=path.join(taskRoot,'openchatcut');
export const defaultManifest=path.join(taskRoot,'hyperframes/edit.json');
export const authorizationPath=path.join(taskWork,'authorization.json');
export const protectedProjectIds=[
 'db290905-d92d-40c3-bf6d-b978bc074d9e',
 'dc02577e-2c3e-435f-9515-51411e73ced4',
 'c094cd11-6065-497c-aaf4-232bc61c9360',
 '9ec9cec9-0a71-43fb-99be-adec9b564c60'
];
export const fileSha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function requireAuthorization(stage,manifestPath=defaultManifest){
 assert(fs.existsSync(authorizationPath),'No OCC write authorization yet; wait for orchestrator B approval and final-media lock.');
 const a=JSON.parse(fs.readFileSync(authorizationPath,'utf8'));
 assert.equal(a.approvedByOrchestrator,'/root');
 assert.equal(a.finalMediaLocked,true,'Final media must be explicitly locked by orchestrator');
 assert.equal(a.designBApproved,true,'Design B must be independently approved');
 assert(a.allowedStages?.includes(stage),`Stage ${stage} not authorized`);
 assert.equal(path.resolve(a.manifestPath),path.resolve(manifestPath),'Authorization manifest mismatch');
 assert.equal(a.manifestSha256,fileSha(manifestPath),'Manifest changed since authorization; request new lock');
 return a;
}
