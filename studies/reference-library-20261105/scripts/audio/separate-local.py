"""Local official audio-separator / ONNX CPU inference. No source upload."""
import os,json,pathlib,sys,time,logging,hashlib
PROJECT=pathlib.Path(__file__).resolve().parents[2]
WORK=PROJECT.parents[1]/'work'/'reference-library-20261105'
AUDIO_WORK=pathlib.Path(os.environ.get('REF_AUDIO_WORK',WORK/'audio-work'))
MANIFEST=pathlib.Path(os.environ.get('REF_AUDIO_MANIFEST',WORK/'manifest.local.json'))
_dll_handles=[]
if os.name=='nt':
    # Reuse the VC runtime already shipped with Codex; only this process sees it.
    runtime=pathlib.Path.home()/'.cache'/'codex-runtimes'/'codex-primary-runtime'/'dependencies'
    for directory in [runtime/'node'/'bin',runtime/'python']:
        if directory.exists(): _dll_handles.append(os.add_dll_directory(str(directory)))
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
os.environ['NUMBA_NUM_THREADS']='2'
os.environ['NUMBA_CACHE_DIR']=str(WORK/'numba-cache')
os.environ['TORCH_HOME']=str(WORK/'torch-cache')
import torch
torch.set_num_threads(2)
torch.set_num_interop_threads(1)
import onnxruntime as ort
_options=ort.SessionOptions
def options():
    result=_options()
    result.intra_op_num_threads=2
    result.inter_op_num_threads=1
    result.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
    return result
ort.SessionOptions=options
from audio_separator.separator import Separator
model='UVR_MDXNET_KARA_2.onnx'
probe='--probe' in sys.argv
out=AUDIO_WORK/('probe-stems' if probe else 'stems')
out.mkdir(parents=True,exist_ok=True)
separator=Separator(model_file_dir=str(WORK/'models'),output_dir=str(out),output_format='WAV',output_single_stem=None if probe else 'Instrumental',use_soundfile=True,log_level=logging.INFO,normalization_threshold=0.95,amplification_threshold=0.0,sample_rate=44100,mdx_params={'hop_length':1024,'segment_size':256,'overlap':0.25,'batch_size':1,'enable_denoise':False})
separator.load_model(model_filename=model)
manifest=json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
selected=[s for s in sys.argv[1:] if s.startswith('V')]
checkpoint=AUDIO_WORK/('separation-probe.json' if probe else 'separation-results.local.json')
records=json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else []
for item in manifest:
    if selected and item['id'] not in selected: continue
    if probe and item['id']!=(selected[0] if selected else 'V01'): continue
    wav=AUDIO_WORK/(item['id']+'.stereo.wav' if not probe else item['id']+'.probe.wav')
    if not wav.exists(): raise FileNotFoundError(str(wav))
    start=time.time()
    cached=out/(item['id']+'.stereo_(Instrumental)_'+pathlib.Path(model).stem+'.wav')
    previous=next((r for r in records if r['id']==item['id']),None)
    if not probe and previous and cached.name in previous.get('files',[]) and cached.exists() and cached.stat().st_size>44:
        print('CACHED '+item['id'],flush=True)
        continue
    else:
        result=separator.separate(str(wav))
    record={'id':item['id'],'elapsed_sec':round(time.time()-start,3),'files':result,'model':model,'provider':'CPUExecutionProvider','threads':2,'probe':probe}
    records=[r for r in records if r['id']!=item['id']]+[record]
    records.sort(key=lambda r:r['id'])
    temporary=checkpoint.with_suffix('.tmp')
    temporary.write_text(json.dumps(records,indent=2),encoding='utf-8')
    temporary.replace(checkpoint)
    print('RESULT '+json.dumps(record),flush=True)
