"""Package the approved editable composition and verify every archived byte."""
from pathlib import Path
import json, hashlib, zipfile, datetime, sys, re
ROOT = Path(__file__).resolve().parents[1]

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

completed = []
for p in sorted((ROOT / 'loops').glob('loop-*/execution.json')):
    if (p.parent / 'review.json').exists(): completed.append((read(p), read(p.parent / 'review.json')))
execution, review = completed[-1]
assert execution['loop'] >= 4 and review.get('status') == 'pass', 'latest real loop must pass independently'
assert sha(ROOT / execution['video']) == execution['sha256']
edit = ROOT / 'hyperframes/edit.json'
assert sha(edit) == execution['editSha256'], 'editable plan drifted after capture'
plan = read(edit)
sys.path.insert(0, str(ROOT / 'hyperframes'))
from composition import build
generated_html = build(plan)[0]
actual_html = (ROOT / 'hyperframes/index.html').read_text(encoding='utf-8')
without_studio_ids = re.sub(r'\sdata-hf-id="[^"]*"', '', actual_html)
assert without_studio_ids == generated_html, 'editable HTML differs beyond Studio element IDs'
generated_sha = hashlib.sha256(generated_html.encode()).hexdigest()
assert (ROOT / 'hyperframes/generated-index.sha256').read_text().strip() == generated_sha
assert (ROOT / 'hyperframes/index.html').read_bytes() == generated_html.encode('utf-8'), 'canonical ZIP must contain exact LF generated HTML without Studio IDs'
files = [p for p in sorted((ROOT / 'hyperframes').rglob('*')) if p.is_file() and not any(x.startswith('.') or x == '__pycache__' for x in p.relative_to(ROOT / 'hyperframes').parts)]
for name in ['docs/操作与学习.md', 'docs/HyperFrames技法实作笔记.md', 'docs/最终剪辑技法对照.md', 'docs/技法选用与难易排行.md', 'docs/四轮改进对照.md']:
    files.append(ROOT / name)
for name in ['reviews/event-clock-boundary-check.json', 'reviews/event-clock-boundary-check.md', 'reviews/studio-annotation-equivalence.json']:
    files.append(ROOT / name)
for a in plan['assets']: assert (ROOT / 'hyperframes' / a['asset']).is_file(), a['asset']
assert (ROOT / 'hyperframes' / plan['audio']['master']).is_file()
for fg in plan.get('foregrounds', []):
    for f in range(fg['start'], fg['end']):
        n = fg.get('offset', 0) + f - fg['start']
        assert (ROOT / f'hyperframes/assets/alpha/{fg["alpha"]}/{n:06}.png').is_file()
members = {p.relative_to(ROOT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files}
archive = ROOT / 'HyperFrames可编辑工程.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as z:
    for p in files: z.write(p, p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == set(members)
    for name, expected in members.items():
        assert z.getinfo(name).file_size == expected['bytes']
        with z.open(name) as f: assert hashlib.file_digest(f, 'sha256').hexdigest() == expected['sha256'], name
report = {'state': 'pass', 'time': datetime.datetime.now().astimezone().isoformat(), 'loop': execution['loop'], 'movieSha256': execution['sha256'], 'editSha256': sha(edit), 'archive': archive.name, 'archiveBytes': archive.stat().st_size, 'archiveSha256': sha(archive), 'crcPassed': True, 'eachArchivedFileShaVerified': True, 'files': members, 'excluded': ['source backups', 'Python bytecode caches', '2 million JPG library', 'render cache', 'original season episodes'], 'scope': 'Complete creation assets and source code; external Python/Node/HF/Chrome/FFmpeg runtimes remain installed dependencies. Native UI validation recorded separately.'}
report['editableMarkupEquivalence']={'generatedSha256':generated_sha,'packagedActualSha256':members['hyperframes/index.html']['sha256'],'studioIdAttributes':actual_html.count('data-hf-id='),'exactGeneratedLfBytesPackaged':True,'policy':'Canonical ZIP contains exact UTF-8 LF build. Studio ID/CRLF variant is preserved separately in evidence; no CSS/GSAP/media/layout differences accepted.'}
(ROOT / 'data/hyperframes-package-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'files'}, ensure_ascii=False))
