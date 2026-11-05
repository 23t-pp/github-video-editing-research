"""Promote the latest independently approved actual loop; no rendering or implied art approval."""
from pathlib import Path
import json, hashlib, shutil
ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()
loop = sorted((ROOT / 'loops').glob('loop-*/execution.json'))[-1].parent
execution, review = read(loop / 'execution.json'), read(loop / 'review.json')
assert execution['loop'] >= 4 and review['status'] == 'pass'
assert review['reviewer'] != execution['executor']
for name, expected in review.get('boundArtifacts', {}).items(): assert sha(ROOT / name) == expected, name
source = ROOT / execution['video']; assert sha(source) == execution['sha256']
quality_path = loop / 'root-machine-check.json'; quality = read(quality_path)
assert quality['machineState'] == 'pass' and quality['sha256'] == execution['sha256']
assert quality['fullDecodedFrames'] == 1440 and quality['decodedAudioSampleFrames'] == 2880000
assert (quality['width'], quality['height'], quality['fps']) == (1920, 1080, 24)
dest = ROOT / '咒力接力_一分钟.mp4'
if dest.exists() and sha(dest) != execution['sha256']:
    history = ROOT / 'renders/canonical-history'; history.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest, history / f'previous-{sha(dest)[:16]}.mp4')
shutil.copy2(source, dest); assert sha(dest) == execution['sha256']
quality.update(file=dest.name, verifiedOriginalLoopFile=execution['video'], verifiedLoopReportSha256=sha(quality_path), promotionPolicy='exact SHA-verified copy after independent pass; same media bytes, no redundant decode claimed')
(ROOT / '成片质量检查.json').write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding='utf-8')
log = quality_path.with_suffix('.loudness.log')
if log.exists(): shutil.copy2(log, ROOT / '成片质量检查.loudness.log')
print(json.dumps({'state':'promoted_independently_approved_movie','file':dest.name,'sha256':sha(dest),'loop':execution['loop']}, ensure_ascii=False))
