from pathlib import Path
import json,copy,hashlib,sqlite3
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
static=read('data/shot-candidates.json');motion={x['id']:x for x in read('data/retrieval-candidates.json')['items']};fresh={x['candidateId']:x for x in read('data/fresh-shot-candidates.json')['items']};corrections={x['candidateId']:x for x in read('data/semantic-corrections.json')['items']}
tail_path=ROOT/'data/tail-action-candidates.json'
tail={x['candidateId']:x for x in read('data/tail-action-candidates.json')['items']} if tail_path.exists() else {}
items=[]
for original in static['items']:
    x=copy.deepcopy(original);cid=x['id'];x['originalStaticObservation']=copy.deepcopy(original)
    if cid in motion:
        m=motion[cid];x['motionPreflight']=m;x['motionDirection']=m.get('motionDirection','unknown');x['motionVerified']=m.get('motionVerified',False)
    if cid in fresh:x['freshWindowEvidence']=fresh[cid]
    if cid in tail:
        t=tail[cid];x['tailActionEvidence']=copy.deepcopy(t)
        x['tailActionEvidence']['scope']='仅该coreSourceSeconds窗口逐原生帧观察；不能把静帧锚点标签扩写为整段剧情身份确认'
        x['tailActionEvidence']['dispatchConstraints']={'scope':'exact coreSourceSeconds only; overrides static anchor guesses inside window','unknownIdentityMustNotBeReplacedByGuessedPersonName':'unknown' in t['characters'],'useCharactersFromThisWindow':True,'finalRetrievalMustUseOriginalVideo':True}
        x['verifiedVisibleMotionInTailWindow']=t['observedMovement']
    if cid in corrections:
        c=corrections[cid];x['semanticCorrection']=c;x['characters']=c['characters'];x['visibleActionOrPose']=c['newLabel'].replace('unknown，','');x['identityConfidence']=c['certainty']
    else:x['identityConfidence']=x.get('semanticConfidence','unknown')
    if cid=='S1C097':x['alphaMotionEvidence']={'report':'evidence/alpha/XCHASE-alpha-report.json','actualMotion':'五个奔跑姿态循环；左右臂交替','preparedSourceStartPTS':764.638875,'preparedFrames':[2,28],'scope':'只对实际分离的26帧，不扩写为整集运动分析'}
    if cid=='S1C020':x['alphaMotionEvidence']={'report':'evidence/alpha/XPALM-alpha-report.json','actualMotion':'手姿大多hold，青焰在变；同号26帧RGBA','scope':'不能把源动画hold说成26个不同动作'}
    episode=f'S1E{x["episode"]:02}';folder=ROOT/'素材集_60Hz_JPG'/episode;db=sqlite3.connect(folder/'index.sqlite');n=round(x['anchorSeconds']*60);row=db.execute('SELECT source_frame,path FROM samples WHERE sample=?',(n,)).fetchone();db.close()
    if row:x['gridLookup']={'sample':n,'nativeFrame':row[0],'jpg':f'素材集_60Hz_JPG/{episode}/{row[1]}'}
    x['dispatchConstraints']={'scope':'static anchor only; precise native window constraints take precedence','finalRetrievalMustUseOriginalVideo':True,'nativeCutAndCropMustBeVerifiedForChosenWindow':True,'unknownIdentityMustNotBeReplacedByGuessedPersonName':'unknown' in x['characters'] or (cid in tail and 'unknown' in tail[cid]['characters'])}
    items.append(x)
sources=['data/shot-candidates.json','data/retrieval-candidates.json','data/fresh-shot-candidates.json','data/fresh-native-verification.json','data/semantic-corrections.json']
if tail_path.exists():sources.append('data/tail-action-candidates.json')
r={'schemaVersion':2,'title':'第一季可调度素材标记：纠正优先的派生catalog','items':items,'count':len(items),'humanStaticAnchors':97,'fourPointMotionPreflight':58,'newNativeFrameReviewedWindows':12,'extraTailNativeFrameReviewedWindows':len(tail),'extraTailNativeFrames':sum(x['decodedNativeFrames'] for x in tail.values()),'unknownIdentityIds':[x['id'] for x in items if 'unknown' in x['characters']],'automaticAppearanceTags':'data/automatic-tags.jsonl','full60HzDataset':'素材集_60Hz_JPG','policy':'原始观察保留；语义纠正优先。窗口预检不自动批准任何更长正式取片。窗口内characters可为unknown，与更早静帧锚点标签分列；调度精确窗口优先使用窗口证据。其余全季画面人物/动作仍未知。','sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}}
r['unknownIdentityIdsScope']='static anchor labels only'
r['unknownTailWindowIdentityIds']=[x['candidateId'] for x in tail.values() if 'unknown' in x['characters']]
(ROOT/'data/material-catalog.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:r[k] for k in ['count','unknownIdentityIds','unknownTailWindowIdentityIds']},ensure_ascii=False))
