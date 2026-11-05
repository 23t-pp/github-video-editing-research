from pathlib import Path
import subprocess,json
BASE=Path(__file__).resolve().parents[2];HF=BASE/'outputs/jjk-edge-v17-v2/hyperframes';EV=HF.parent/'evidence'
NODE='C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
p=subprocess.run([NODE,str(HF/'hf.mjs'),'lint','.','--json'],cwd=HF,capture_output=True)
(EV/'HyperFrames-lint.log').write_bytes(p.stdout+p.stderr)
r=json.loads(p.stdout);assert p.returncode==0 and r['errorCount']==0
print(json.dumps({k:r[k] for k in ['ok','errorCount','warningCount']},ensure_ascii=False),flush=True)
p=subprocess.run([NODE,str(HF/'hf.mjs'),'validate','.','--timeout','5000'],cwd=HF,capture_output=True)
(EV/'HyperFrames-runtime-validate.log').write_bytes(p.stdout+p.stderr)
print('validate exit',p.returncode,flush=True)
print((p.stdout+p.stderr).decode(errors='replace')[-2000:])
assert p.returncode==0
