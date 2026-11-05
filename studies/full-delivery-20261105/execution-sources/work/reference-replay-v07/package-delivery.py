"""Package the verified V07 project without render caches or whole source films."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json, re, zipfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2] / 'outputs' / 'reference-replay-next'
STAMP = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

ui = {
    'recordedAt': STAMP,
    'method': '实际浏览器界面检查；界面截图保存在 evidence/ui。',
    'openchatcut': {
        'importedProjectId': 'd55540ff-ec35-4489-ae3f-a9192cdbe3f5',
        'officialImport': {'mediaRestored': 45, 'missingMedia': 0, 'evidence': 'openchatcut/官方工程包导入回验.json'},
        'hfSequencePlayback': '已点击播放并观察时间推进至16秒附近，预览出现实际车祸镜头；随后暂停。',
        'nativeSequence': '已打开02原生逐镜序列，在18.55秒选择P17-replacement.mp4；实际显示黄紫双车镜头。',
        'editableProperties': '已打开片段属性，源区间12–37帧、1倍速，以及位置、尺度、旋转等参数控件可见。',
        'timing': {'fps': 25, 'totalFrames': 750, 'durationSeconds': 30, 'nativeShots': 32, 'hfSegments': 15},
        'dragOrParameterChangeTestPerformed': False,
        'proof': 'evidence/ui/OpenChatCut原生工程.png'
    },
    'hyperframes': {
        'previewUrl': 'http://127.0.0.1:5215',
        'seekSeconds': 26.68,
        'observed': '侧窗内出现下一镜汽车画面。选中Window New Plane图层，右侧显示可编辑样式、1920×800布局及9个Motion效果。',
        'lint': {'errors': 0, 'warnings': 3, 'scope': '真实CLI lint与Studio界面；有意复用的8片放射视频及两个密集透明图层轨道。'},
        'duplicateEntryResolved': '旧HTML备份已存为.source-backups/*.html.bak，仅index.html作为作品入口。',
        'proof': 'evidence/ui/HyperFrames侧窗图层.png'
    },
    'comparisonPlayer': {
        'url': 'http://127.0.0.1:5216',
        'playback': '已点击同步播放，两个video均在推进，主片有声轨且未静音，参考默认静音；无媒体错误。',
        'frameStep': '从26.60秒连续点击两次下一帧，显示26.68秒、F667。',
        'domCurrentTimeSeconds': {'movie': 26.6801, 'reference': 26.6801},
        'decodedDurationSeconds': {'movie': 30, 'reference': 30.04},
        'proof': 'evidence/ui/成片逐帧对照.png'
    },
    'auditoryListeningPerformed': False,
    'limits': '界面已播放和显示画面；制作代理没有实际听觉试听，也未在验收时拖动或修改镜头参数。音频同步测量见质量检查.json。'
}
write_json(ROOT / 'UI验收.json', ui)

intro = '''# 《越界》V07 · HyperFrames可编辑工程

这是30秒、25fps的《速度与激情》混剪工程。音乐选自既有音乐库V07候选，片长跟随这条音乐。

## 从这里开始

1. 阅读 [中文学习总结](学习总结与命令.md)，了解每个步骤和命令的作用。
2. 打开 [工程说明](hyperframes/README.md)，按说明启动本地HyperFrames预览。
3. 查看 [六组转场对照](evidence/六组转场对照.jpg) 与 [逐段拆解](evidence/参考拆解与配对.md)。

工程内含已裁取的素材、库内音乐、五组动态透明PNG、侧窗跟踪数据、HTML/GSAP与生成/渲染脚本。无需整部电影即可预览和再渲染。渲染需要本机Python、Node、HyperFrames CLI、FFmpeg和Chrome；本机路径和换电脑时的调整方法见工程说明。

这个包只含HyperFrames工程与教程。最终MP4和OpenChatCut `.ccproj` 在外部交付目录单独提供；不包含整部电影、渲染缓存或旧HTML备份。

## 可编辑边界

镜头和效果数据入口为 `hyperframes/edit.json`；透明前景在 `hyperframes/assets/alpha`；侧窗控制点与逐帧矩阵在 `hyperframes/motion`。先复制一份，再练习修改参数。

本片复刻参考的层次与转场结构，不等于逐像素还原。真人手势、扇面变形、弧形窗沿与复杂遮挡仍有差异。电影原有爆炸与飞车不是本次新建的CG。

## 检查范围

成片750帧已解码，工程已在真实HyperFrames Studio打开，侧窗图层与预览已检查。三项lint警告为有意重复视频和密集alpha轨道；没有lint错误。声音做过采样、响度和同步测量，未声称已完成听觉试听。实测范围见 [质量检查](质量检查.json) 与 [UI验收](UI验收.json)。
'''

archive = ROOT / 'HyperFrames可编辑工程.zip'
skip_dirs = {'.hyperframes', '.thumbnails', '.waveform-cache', '__pycache__', '.render-cache', '.source-backups', 'node_modules', '.git'}
files = []
for directory in ['hyperframes', 'evidence']:
    for file in sorted((ROOT / directory).rglob('*')):
        rel = file.relative_to(ROOT)
        if file.is_file() and not any(part in skip_dirs for part in rel.parts) and file.suffix != '.pyc':
            files.append((file, rel.as_posix()))
for name in ['学习总结与命令.md', '随机参考抽选.json', '默认混剪规则.md', '质量检查.json', 'UI验收.json', '成片验证.json']:
    files.append((ROOT / name, name))
manifest = [{'path': name, 'bytes': file.stat().st_size, 'sha256': digest(file)} for file, name in files]
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=4) as package:
    package.writestr('README.md', intro)
    for file, name in files:
        package.write(file, name)
    package.writestr('文件校验清单.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(archive) as package:
    bad = package.testzip()
    assert bad is None, bad
    names = package.namelist()
    assert len(names) == len(set(names))
    assert 'hyperframes/index.html' in names and 'hyperframes/assets/audio/master.wav' in names
    assert not any('/.render-cache/' in n or n.endswith('.html.bak') for n in names)
write_json(ROOT / 'HyperFrames工程包核验.json', {
    'recordedAt': STAMP, 'file': archive.name, 'bytes': archive.stat().st_size,
    'sha256': digest(archive), 'entries': len(names), 'zipCrcCheck': 'passed',
    'omitted': sorted(skip_dirs), 'contentHashesInside': '文件校验清单.json'
})

occ = next((ROOT / 'openchatcut').glob('*.ccproj'))
deliverables = [ROOT / '越界_V07复刻.mp4', occ, archive, ROOT / 'README.md', ROOT / '学习总结与命令.md', ROOT / '观看与对照.html']
write_json(ROOT / '交付清单.json', {
    'recordedAt': STAMP,
    'reference': 'V07，续用原抽选，未重抽',
    'bgm': '既有音乐库V07__music-candidate.m4a；保持原速，去掉尾部8个极低电平采样帧并固定降6.4dB',
    'originalAudioDurationSeconds': 30.0001814059,
    'outputDurationSeconds': 30,
    'durationDifferenceMilliseconds': -0.1814059,
    'files': [{'path': f.relative_to(ROOT).as_posix(), 'bytes': f.stat().st_size, 'sha256': digest(f)} for f in deliverables]
})

missing = []
for doc in [ROOT/'README.md', ROOT/'evidence/参考拆解与配对.md']:
    for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
        if not link.startswith(('http:', 'https:', '#')) and not (doc.parent / unquote(link.split('#')[0])).exists():
            missing.append([doc.name, link])
assert not missing, missing
print(json.dumps({'package': archive.name, 'bytes': archive.stat().st_size, 'entries': len(names), 'zipCrcCheck': 'passed', 'documentLinkCheck': 'passed'}, ensure_ascii=False))
