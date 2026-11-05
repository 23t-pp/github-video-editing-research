from pathlib import Path
from fractions import Fraction
from datetime import datetime,timezone,timedelta
from PIL import Image
import hashlib,json,sqlite3,time
R=Path(__file__).resolve().parents[1];LIB=R/'素材集_60Hz_JPG';start=time.time()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cfg=sha(R/'data/run-config.json');overall=json.loads((R/'data/library-verification.json').read_text(encoding='utf-8'));rawsum=json.loads((R/'data/library-summary.json').read_text(encoding='utf-8'))
assert overall['state']=='pass' and overall['verifiedEpisodes']==24 and rawsum['state']=='complete'
checks=[];sampled=[]
for i in range(1,25):
    eid=f'S1E{i:02}';F=LIB/eid;raw=json.loads((F/'progress.json').read_text(encoding='utf-8'));q=json.loads((F/'verification.json').read_text(encoding='utf-8'))
    assert raw['state']=='complete' and q['state']=='pass' and raw['configSha256']==q['configSha256']==cfg
    assert raw['sourceSha256']==q['sourceSha256']
    assert all(q[k]==0 for k in ['missing','extra','corruptUniqueJpeg','badAlias'])
    assert q['nativeJpegDecodedAndShaChecked']==raw['nativeFramesDecoded']
    assert q['allSamplePathsAndPtsChecked']==q['physicalJpgEntries']==q['expected']==raw['expectedSamples']==raw['samplesWritten']
    assert sha(F/q['fullJsonlExport'])==q['fullJsonlSha256']
    db=sqlite3.connect(f'file:{(F/"index.sqlite").as_posix()}?mode=ro',uri=True)
    n=raw['expectedSamples'];assert db.execute('SELECT COUNT(*),MIN(sample),MAX(sample),SUM(duplicate) FROM samples').fetchone()==(n,0,n-1,raw['duplicateEntries'])
    assert db.execute('SELECT COUNT(*) FROM native').fetchone()[0]==raw['nativeFramesDecoded']
    tb=Fraction(raw['sourceTimeBase']);first=raw['firstSourcePts']
    for s in sorted({0,n//2,n-1}):
        sf,dup,path=db.execute('SELECT source_frame,duplicate,path FROM samples WHERE sample=?',(s,)).fetchone();pts,h,primary=db.execute('SELECT pts,jpeg_sha256,first_path FROM native WHERE frame=?',(sf,)).fetchone()
        assert s*tb.denominator>=(pts-first)*tb.numerator*60
        if sf+1<raw['nativeFramesDecoded']:
            nxt=db.execute('SELECT pts FROM native WHERE frame=?',(sf+1,)).fetchone()[0];assert s*tb.denominator<(nxt-first)*tb.numerator*60
        a,b=(F/path).stat(),(F/primary).stat();assert (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino) or sha(F/path)==h
        assert sha(F/path)==h
        with Image.open(F/path) as im:im.load();assert im.size==(640,360) and im.format=='JPEG'
        sampled.append({'episode':eid,'sample':s,'sourceFrame':sf,'jpg':str((F/path).relative_to(R).as_posix()),'checks':'rational PTS interval, full pixel load, SHA and alias ID/content'})
    db.close();checks.append({'episode':eid,'samples':n,'uniqueNative':raw['nativeFramesDecoded'],'duplicates':raw['duplicateEntries'],'rawReportSha256':sha(F/'progress.json'),'verificationReportSha256':sha(F/'verification.json'),'jsonlSha256':q['fullJsonlSha256'],'reportedFullDecodeAndAllAliasPass':True})
assert sum(x['samples'] for x in checks)==2061018==overall['samples']
assert sum(x['uniqueNative'] for x in checks)==823577==overall['uniqueJpegFullDecode']
assert sum(x['duplicates'] for x in checks)==1237441
report={'reviewer':'/root/s1_design_auditor','status':'pass','phase':'physical_material_dataset_only','reviewedAt':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'boundArtifacts':{str(p.relative_to(R).as_posix()):sha(p) for p in [R/'data/run-config.json',R/'data/library-summary.json',R/'data/library-verification.json',R/'scripts/extract-library.py',R/'scripts/verify-library.py']},'episodes':24,'jpgSamplePaths':2061018,'uniqueNativeJpeg':823577,'repeatedSamplePaths':1237441,'reportedAllUniquePixelDecodeAndSha':823577,'reportedAllSampleFileIdAndPtsChecks':2061018,'independentReviewScope':'Read and cross-check all24 raw/verification reports, all JSONL SHA, all SQLite count/range/duplicate totals; independently full pixel decode+SHA+alias/PTS samples first/middle/last per episode (72 samples). Did not wastefully repeat full-season decoding performed by verifier.','independentSampleCount':len(sampled),'episodeReports':checks,'independentSamples':sampled,'knownScopeLimits':['640x360 q6 JPG are analysis proxies; high-quality film retrieves original 1920x1080 sources','60Hz paths include repeated source frames through hardlinks; they are not2061018 unique action frames or interpolation','automatic per-second RGB/luma labels are deterministic technical metadata, not verified character/action semantics','semantic curated candidates and final film remain separately reviewed; material pass does not pass all four loops or final film'],'elapsedSeconds':time.time()-start}
(R/'reviews/素材集最终审核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','episodes':24,'paths':2061018,'unique':823577,'independentSampleCount':len(sampled),'elapsedSeconds':report['elapsedSeconds']},ensure_ascii=False))
