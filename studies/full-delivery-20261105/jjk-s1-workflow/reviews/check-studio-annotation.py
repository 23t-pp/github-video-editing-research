from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parents[1];d=R/'evidence/ui/studio-annotation-drift';a=(d/'studio-open-normalized.html').read_bytes();b=(d/'expected-frozen-build.html').read_bytes();c,n=re.subn(rb'\sdata-hf-id="[^"]*"',b'',a)
r={'reviewer':'/root/s1_design_auditor','status':'pass_metadata_equivalence_only','expectedRawBytes':len(b),'studioRawBytes':len(a),'hfIdRemoved':n,'cleanedRawEqualsExpected':c==b,'expectedRawSHA':hashlib.sha256(b).hexdigest(),'cleanedRawSHA':hashlib.sha256(c).hexdigest(),'rawStudioSHA':hashlib.sha256(a).hexdigest(),'scope':'Only exactly448 data-hf-id attributes stripped; raw bytes must equal expected frozen build. No CSS/GSAP/media content tolerance.','deliveryRecommendation':'Archive canonical raw index.html separately from live Studio annotation. Keep both evidence HTMLs and this proof. Do not rerender just for editor IDs.'}
assert n==448 and c==b
r['snapshotSerialization']='Two saved HTML evidence files use CRLF42 lines; expected canonical build uses LF. LF normalization only is recorded separately from attribute equivalence.'
r['canonicalLFBytes']=len(b.replace(b'\r\n',b'\n'))
r['canonicalLFSha256']=hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()
r['studioLFSha256']=hashlib.sha256(a.replace(b'\r\n',b'\n')).hexdigest()
assert r['canonicalLFSha256']==json.loads((d/'check.json').read_text(encoding='utf-8'))['expectedSha256']
(R/'reviews/studio-annotation-equivalence.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False))
