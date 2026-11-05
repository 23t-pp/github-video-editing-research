import assert from 'node:assert/strict';
export function assertTaskWriteTarget(target,ownProjectId,priorHashes,protectedIds){
 assert.equal(target,ownProjectId,'Only this S1 task new UUID may receive edit-tool writes');
 assert(!protectedIds.includes(target),'Fixed prior V1/V2 project is protected');
 assert(!Object.hasOwn(priorHashes,target),'S1 must never reuse a pre-existing project UUID');
}
export function classifyPriorProjectHashes(prior,current,protectedIds){
 const checks=Object.entries(prior).map(([id,before])=>({projectId:id,beforeSha256:before,afterSha256:current[id]??null,equal:before===current[id],strictProtected:protectedIds.includes(id)}));
 for(const c of checks.filter(c=>c.strictProtected))assert(c.equal,`Fixed protected project ${c.projectId} changed; stop, never restore or overwrite it`);
 return {checks,fixedProtectedProjectsUnchanged:true,unchangedProjects:checks.filter(c=>c.equal).length,externalConcurrentChanges:checks.filter(c=>!c.equal&&!c.strictProtected).map(c=>({...c,classification:'external_branch_concurrent_drift',attribution:'No write by this task is authorized to this UUID; difference alone does not prove which external branch made it',action:'record_only_no_restore_no_overwrite'}))};
}
