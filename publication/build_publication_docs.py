"""Build the public download hub from verified staging metadata; never upload assets.

Run from any directory with a usable Python 3.11+:
python publication/build_publication_docs.py --workspace D:/path/to/production-workspace
Add --final only after all 24 JPG archives have passed their actual verification.
The script writes only its own publication/ directory. Copied evidence keeps source bytes.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path
from urllib.parse import unquote

REPO = '23t-pp/github-video-editing-research'
WEB = f'https://github.com/{REPO}'
PROJECT_TAG = 'editing-projects-2026-11-05'
JPG_TAG = 'jjk-s1-jpg-60hz-2026-11-05'
HERE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def link(name, tag=PROJECT_TAG):
    return f'[{name}]({WEB}/releases/download/{tag}/{name})'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=HERE.parents[2])
    parser.add_argument('--final', action='store_true', help='Require 24 verified JPG archives and exact full-season manifest')
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    staging = workspace/'work/publish-all-20261105'
    projects, jpg = staging/'projects', staging/'jpg'
    assets = read(projects/'assets-manifest.json')
    summary = read(projects/'final-delivery-summary.json')
    assert len(assets) == 25 and sum(a['bytes'] for a in assets) == 6996473739
    assert summary['state'] == 'COMPLETE' and summary['text_mirror_files'] == 5966
    for a in assets:
        ready = projects/'ready'/f"{a['asset']}.json"
        assert ready.is_file(), f'Missing ready marker: {ready}'
        r = read(ready)
        assert r['bytes'] == a['bytes'] and r['sha256'] == a['sha256'], a['asset']

    episodes = []
    for number in range(1, 25):
        path = jpg/f'S1E{number:02d}.verified.json'
        if not path.exists():
            continue
        entry = read(path)
        assert entry['state'] == 'pass'
        archive = jpg/entry['archive']
        assert archive.is_file() and archive.stat().st_size == entry['archiveBytes']
        assert entry['jpgPaths'] == entry['regularJpegs'] + entry['hardlinkJpegs']
        episodes.append(entry)
    manifest_path = jpg/'jpg-manifest.json'
    remote = read(staging/'remote-uploads.json') if (staging/'remote-uploads.json').exists() else {'results': {}}
    if args.final:
        assert len(episodes) == 24, f'Final publication requires 24 verified episodes; found {len(episodes)}'
        assert manifest_path.is_file(), 'Run finalize_jpg.py first'
        manifest = read(manifest_path)
        assert manifest['state'] == 'pass' and manifest['episodesCount'] == 24
        assert (manifest['jpgPaths'], manifest['sourceFrameIds'], manifest['hardlinkJpegs']) == (2061018, 823577, 1237441)
        for entry in episodes:
            assert entry in manifest['episodes'], entry['id']
        assert remote.get('state') == 'complete', 'Final publication requires uploader state complete after queue sealing'
        assert remote.get('verifiedAssets') == 57 and len(remote.get('results', {})) == 57, 'Final publication requires exactly 57 remotely verified assets'
        assert not remote.get('errors') and remote.get('queuedOrRunning') == 0
        seal = read(staging/'upload-queue-sealed.json')
        assert len(seal['expectedKeys']) == 57 and set(seal['expectedKeys']) == set(remote['results'])
        for item in remote['results'].values():
            assert item['state'] == 'remote_verified' and item['remoteSize'] == item['bytes'] and item['remoteDigest'] == 'sha256:'+item['sha256'], item['name']
        assert (staging/'publication-evidence-local-manifest.json').is_file(), 'Audit evidence archive metadata is required'

    # Preserve every copied source byte and record where it came from.
    copied = []
    def copy(source, relative):
        destination = HERE/relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        digest = sha(source)
        assert sha(destination) == digest
        copied.append({'source': source.relative_to(workspace).as_posix(), 'path': relative, 'bytes': source.stat().st_size, 'sha256': digest})

    copy(projects/'assets-manifest.json', 'manifests/assets-manifest.json')
    copy(projects/'final-delivery-summary.json', 'manifests/final-delivery-summary.json')
    for source in sorted((projects/'manifests').glob('*.json')):
        copy(source, 'manifests/projects/'+source.name)
    for source in sorted((projects/'docs').iterdir()):
        if source.is_file() and source.suffix in {'.md', '.json'}:
            copy(source, 'evidence/projects/'+source.name)
    for name in ('restore_projects.py', 'package_projects.py', 'package_app.py', 'package_supplement.py', 'finalize_publication.py', 'test_restore_projects.py'):
        copy(projects/name, 'tools/'+name)
    for name in ('validation-summary.json', 'outputs-coverage-verification.json', 'restore-tests.json', 'exclusions.json'):
        copy(projects/name, 'evidence/projects/'+name)
    for name in ('restore_jpg.py', 'pack_jpg.py', 'finalize_jpg.py', 'test_restore_jpg.py'):
        copy(jpg/name, 'tools/'+name)
    for name in ('README_JPG.zh-CN.md', 'restore-smoke-test.json', 'RECOVERY_EVENTS.json'):
        if (jpg/name).exists():
            copy(jpg/name, 'evidence/jpg/'+name)
    for entry in episodes:
        name = entry['id']+'.verified.json'
        copy(jpg/name, 'evidence/jpg/'+name)
    for name in ('jpg-manifest.json', 'SHA256SUMS-JPG.txt', 'JPG-ARCHIVES.csv'):
        if (jpg/name).exists():
            copy(jpg/name, 'manifests/'+name)
    for source in sorted((staging/'audit').iterdir()):
        if source.is_file() and source.suffix in {'.py', '.json', '.md'}:
            copy(source, ('tools/independent/' if source.suffix == '.py' else 'evidence/independent/')+source.name)
    if (staging/'publication-evidence-local-manifest.json').exists():
        copy(staging/'publication-evidence-local-manifest.json', 'manifests/publication-evidence-local-manifest.json')
    if (staging/'verify_public_delivery.py').exists():
        copy(staging/'verify_public_delivery.py', 'tools/verify_public_delivery.py')
    for name in ('publish-actions.json', 'public-delivery-verification.json', '发布操作与命令学习.zh-CN.md'):
        if (staging/name).exists():
            copy(staging/name, 'evidence/independent/'+name)
    # Deliberately omit machine paths from this public remote snapshot.
    remote_records = [{k:v for k,v in r.items() if k != 'path'} for r in remote.get('results', {}).values()]
    write_json(HERE/'manifests/remote-assets-snapshot.json', {'scope':'Snapshot of uploader size/digest comparisons; draft/public visibility is managed separately', 'assets':remote_records})
    by_remote = {r['name']:r for r in remote_records}
    remote_projects = [r for r in remote_records if r.get('release') == 'projects']
    remote_jpg = [r for r in remote_records if r.get('release') == 'jpg']
    if args.final:
        assert (len(remote_projects), len(remote_jpg)) == (27, 30)
        assert sum(r['bytes'] for r in remote_records) == 21650704440
    jpg_heading = '全季 JPG：24集下载表' if args.final else '全季 JPG：24集预期下载表'
    jpg_anchor = '#全季-jpg24集下载表' if args.final else '#全季-jpg24集预期下载表'

    lines = [
        '# 成片、完整工程与全季 JPG 下载中枢', '',
        '先看成片，再下载对应工程。**Git 浏览页只保存源码和文档；MP4、可编辑工程和 JPG 实物在 Release 附件。** 原封存 README 里的相对 MP4、ZIP、图片链接，在 Git 文本镜像中可能没有对应文件；请从本页下载完整包并恢复到本地后使用原说明。', '',
        f'[工程成果 Release]({WEB}/releases/tag/{PROJECT_TAG}) · [全季 JPG Release]({WEB}/releases/tag/{JPG_TAG}) · [仓库首页](../README.md)', '',
        ('**完整交付：24/24集归档、全季清单与57项Release附件均通过校验。** 本页记录工程与素材的准确下载名、字节数、SHA及还原方法；远端附件核验快照见下文。' if args.final else f'**准备中：目前 {len(episodes)}/24 集归档完成本地校验。下方始终列出24集预期文件名，尚未完成的条目不代表已可下载；两个 Release 公开前，外部读者也无法访问草稿附件。**'), '',
        '## 只想先看成片', '',
        f'{link("jjk-s1-final-60s.mp4")}：咒术第一季 V20《咒力接力》，1920×1080、24fps、1440帧、60秒，50,762,462字节。SHA-256：`90d75e559b81c4c2978fd733aaa1206b5d03b8a73141b4cb1442ef9b91af682d`。它是独立预览附件，也在 S1 完整包内。', '',
        '## 每个项目要下载哪些包', '',
        '“完整包”保留该项目交付目录；表中列出的 HF/OCC 独立附件也必须下载到同一下载目录，还原脚本会按原文件名回填。HF 指 HyperFrames，OCC 指 OpenChatCut。S1 的全季 JPG 另行下载；播放成片和打开内嵌媒体的 OCC 工程不必先下载全部 JPG。', '',
        '|项目|完整包（字节）|还要下载的独立工程附件|', '|---|---|---|',
    ]
    labels = {'openchatcut-local':'OpenChatCut 本机桥接说明','reference-editing-study':'参考剪辑学习研究','reference-library-20261105':'20条参考、音乐与技法学习库','v05-six-panel':'V05 六格分屏复刻','fast60':'速度与激情一分钟','reference-replay-next':'V07 随机抽选复刻','jjk-edge-v17':'EDGE V1','jjk-edge-v17-v2':'EDGE V2 精修','jjk-edge-v17-v3-dedup':'EDGE V3 去重（EDGE 最新）','reference-library-release-20261105':'初次参考库发布记录','jjk-s1-workflow':'咒术第一季 V20（独立任务，L4封存）'}
    complete = [a for a in assets if a['asset'].endswith('-complete.zip')]
    for asset in complete:
        key = asset['asset'].removesuffix('-complete.zip')
        external = asset.get('restore', {}).get('external_assets', [])
        downloads = [link(x['asset']) for x in external if 'asset' in x]
        if any('release' in x for x in external):
            downloads.append(f'[JPG 24集（按需）]({jpg_anchor})')
        lines.append(f"|{labels[key]}|{link(asset['asset'])}<br>{asset['bytes']:,}|{'<br>'.join(downloads) or '无独立回填附件'}|")
    lines.extend(['', '以上11个完整包和8个独立 HF/OCC 附件属于25项工程资产。其余6项如下：', '', '|附件|用途|字节|', '|---|---|---|'])
    other_names = {'execution-and-research-sources.zip':'执行脚本、研究快照与许可来源（`--with-sources`）','openchatcut-app-source-snapshot.zip':'OpenChatCut 应用源码快照（`--with-sources`）','publication-supplement.zip':'169个非秘密源文件补包；S1恢复必需','restore_projects.py':'自动恢复完整包与独立附件','download-and-restore.zh-CN.md':'原版中文下载恢复指南（下面的本页命令优先）','project-release-tools-and-manifests.zip':'42个发布工具、逐文件清单与验收元数据'}
    for asset in assets:
        if asset['asset'] in other_names:
            lines.append(f"|{link(asset['asset'])}|{other_names[asset['asset']]}|{asset['bytes']:,}|")
    lines.extend(['', '25项共 **6,996,473,739字节**；独立预览 MP4 和独立审计证据 ZIP 另计。精确 SHA、回填路径见 [工程资产清单](manifests/assets-manifest.json)，逐文件清单见 [清单目录](manifests/projects/)。源文件和原说明的字节保持不变，复制记录见 [copy-integrity.json](manifests/copy-integrity.json)。', '',
        ('工程 Release 共 **27附件 / 7,048,393,867字节**（25项工程资产 + 预览MP4 + 独立审计ZIP）；JPG Release 共 **30附件 / 14,602,310,573字节**（24档JPG + 6份工具/清单）。两者合计 **57附件 / 21,650,704,440字节**。' if args.final else '最终总览将在57项附件和远端校验全部完成后生成。'), '',
        '## Windows 完整下载和恢复', '',
        '先在 PowerShell 执行 `python --version` 和 `gh --version` 检查已有工具。下文 `python` 指你机器上可用的 Python 3.11+；已有 Python 或软件随附运行时时可直接使用其完整路径，无须重装。若命令不存在，再安装 [Python](https://www.python.org/downloads/windows/) 或 [GitHub CLI](https://cli.github.com/)。GitHub 要求登录时运行 `gh auth login`。也可在 Release 页面逐项点击下载附件。', '',
        '以下示例恢复到新目录。先下载工程、全部实物与工具，再恢复；`git clone` 不会下载这些附件。', '', '```powershell',
        'New-Item -ItemType Directory -Force -Path D:/video-backup/packages | Out-Null',
        f'gh release download {PROJECT_TAG} --repo {REPO} --dir D:/video-backup/packages',
        f'gh release download {JPG_TAG} --repo {REPO} --dir D:/video-backup/packages',
        'Set-Location D:/video-backup/packages',
        'python -X utf8 ./restore_projects.py --downloads . --workspace D:/video-backup/workspace --with-sources',
        'python -X utf8 ./restore_jpg.py . --destination D:/video-backup/workspace/outputs/jjk-s1-workflow/素材集_60Hz_JPG --manifest ./jpg-manifest.json', '```', '',
        '工程脚本会核验下载清单（同目录存在时）以及独立附件 SHA，按嵌入映射回填 HF/OCC。已有同内容文件会跳过，已有不同内容会报错。`--with-sources` 还原执行源码及 `dependencies/OpenChatCut-main`；不传则只恢复工程。下载重跑可加 `gh` 的 `--skip-existing`，随后必须让恢复脚本核 SHA，确保没有残缺附件。', '',
        '只要 S1：下载表内 S1 的三个包、`publication-supplement.zip`、`restore_projects.py`（建议同时下载资产清单），然后运行：', '', '```powershell',
        'python -X utf8 ./restore_projects.py --downloads . --workspace D:/video-backup/workspace --project jjk-s1-workflow', '```', '',
        '恢复后打开 `outputs/jjk-s1-workflow/README.md`；正式片为 `咒力接力_一分钟.mp4`。HF ZIP 在项目根，OCC 在 `openchatcut`。四轮实际视频、独立审核与修订保留在原目录；EDGE V1/V2/V3 与第一季项目互相独立。', '',
        '## '+jpg_heading, '',
        '目标为 **2,061,018个 JPG 采样路径 = 823,577个源帧 JPEG + 1,237,441个重复采样路径**。640×360/q6，源片为24000/1001fps，60Hz表示采样网格，没有插帧。重复路径存为 tar 硬链接；全部路径都会恢复。每档内还包含 SQLite、逐样本 JSONL 及真实校验元数据。高分辨率剪辑需要回原视频取片。', '',
        '|集|归档下载|字节|JPG路径|源 JPEG|硬链接|校验状态|', '|---|---|---:|---:|---:|---:|---|'])
    by_ep = {x['id']: x for x in episodes}
    for number in range(1,25):
        key = f'S1E{number:02d}'
        entry = by_ep.get(key)
        if entry:
            remote_entry = by_remote.get(entry['archive'], {})
            remote_ok = remote_entry.get('state') == 'remote_verified' and remote_entry.get('remoteSize') == entry['archiveBytes'] and remote_entry.get('remoteDigest') == 'sha256:'+entry['archiveSha256']
            status = '本地通过；远端大小/SHA通过' if remote_ok else '本地通过；远端待核'
            lines.append(f"|{key}|{link(entry['archive'], JPG_TAG)}|{entry['archiveBytes']:,}|{entry['jpgPaths']:,}|{entry['regularJpegs']:,}|{entry['hardlinkJpegs']:,}|{status}|")
        else:
            lines.append(f"|{key}|{link(key+'.tar.gz', JPG_TAG)}（预期）|待生成|待核|待核|待核|尚未完成|")
    lines.extend(['', '恢复还需同一 Release 的 `restore_jpg.py`、`jpg-manifest.json`；另提供 `SHA256SUMS-JPG.txt`、`JPG-ARCHIVES.csv`、`pack_jpg.py`、`README_JPG.zh-CN.md`。'+('全季归档共 **'+f"{manifest['archiveBytes']:,}"+'字节**。' if args.final else '全季清单在24集全部完成后生成。'), '',
        '只恢复一集：', '', '```powershell',
        'python -X utf8 ./restore_jpg.py ./S1E01.tar.gz --destination D:/video-backup/workspace/outputs/jjk-s1-workflow/素材集_60Hz_JPG --manifest ./jpg-manifest.json', '```', '',
        '归档里直接是 `S1E01/minute-000/F0000000.jpg`，目标必须止于 `素材集_60Hz_JPG`，不要再加一层 S1E01。中断后加 `--resume`；硬链接失败会自动复制，也可加 `--copy`。复制会多占空间。若要单独修改某张硬链接图片，先复制为独立文件。', '',
        '## 阅读源码、核验与复现', '',
        '[Git小文本镜像](../studies/full-delivery-20261105/)有5,966份源码与文档，85,479,450字节。[文本镜像清单](manifests/projects/text-mirror-manifest.json)记录各文件；媒体缺席是发布分层，不能用 Git 页面相对链接是否打开判断工程缺失。完整包恢复后按原 README 使用。', '',
        '本目录的 [恢复与打包工具](tools/) 和 [原始验收证据](evidence/) 是小文本副本。工程包逐条目核过 bytes/SHA/CRC，恢复冒烟测试覆盖2,356个文件并复跑。JPG逐档报告见 [JPG证据](evidence/jpg/)。[远端资产快照](manifests/remote-assets-snapshot.json)记录附件的 GitHub 大小和 digest 对比。快照核验附件内容，公开访问核验另由发布后的匿名检查记录。', '',
        f'完整独立审计材料：{link("publication-audit-evidence.zip")}。它与25项工程资产分开计数，保留打包来源、全24集独立归档检查、OCC runtime检查、原文件覆盖、源码配置审查和发布前远端核验。可在线阅读 [独立审计证据](evidence/independent/) 与 [独立审计工具源码](tools/independent/)。工具保留原字节及原制作工作区的路径假设，复查时按文件头配置工作区；完整证据ZIP保留原相对目录。', '',
        ('审计ZIP：**'+f"{by_remote['publication-audit-evidence.zip']['bytes']:,}"+'字节**，SHA-256：`'+by_remote['publication-audit-evidence.zip']['sha256']+'`。' if args.final else '审计ZIP字节与SHA在最终远端核验后列出。'), '',
        '发布者的匿名公开访问核验代码：[verify_public_delivery.py](tools/verify_public_delivery.py)。公开发布后的最终报告保存在 [独立审计证据目录](evidence/independent/)；发布前报告的 `remotePublicVerified: false` 仅描述当时草稿状态，不能当作公开访问验收结果。', '',
        ('[本次发布操作与命令学习](evidence/independent/发布操作与命令学习.zh-CN.md)逐步解释打包、硬链接、上传校验、Git推送、公开访问检查和恢复命令。' if (staging/'发布操作与命令学习.zh-CN.md').exists() else ''), '',
        '主要 alpha、撕边、大字等复杂合成回 HF 编辑；OCC 原生镜头负责顺序、裁切、音轨，两者不自动双向同步。依赖和应用本体按原项目说明配置；已保留上游许可证、固定版本及研究快照来源。原工程中的制作机绝对路径要按本机安装位置修改。', '',
        '原始资料副本：[工程中文指南](evidence/projects/download-and-restore.zh-CN.md)、[JPG中文指南](evidence/jpg/README_JPG.zh-CN.md)。维护者可用 [build_publication_docs.py](build_publication_docs.py) 重生成本页；`--final` 要求24集精确总数、封闭队列和57项远端校验完成。静态文档审查由 [audit_publication_docs.py](audit_publication_docs.py) 执行。', '',
    ])
    if manifest_path.exists():
        lines.extend(['全季生成清单：[jpg-manifest.json](manifests/jpg-manifest.json) · [SHA256SUMS-JPG.txt](manifests/SHA256SUMS-JPG.txt) · [JPG-ARCHIVES.csv](manifests/JPG-ARCHIVES.csv)', ''])
    (HERE/'README.md').write_text('\n'.join(lines), encoding='utf-8')
    write_json(HERE/'manifests/copy-integrity.json', {'scope':'Byte-preserved source copies in publication only', 'files':copied})
    # Check every relative Markdown link in the generated hub. Auto anchors need no file.
    checked = []
    for target in re.findall(r'\]\(([^)]+)\)', (HERE/'README.md').read_text(encoding='utf-8')):
        if target.startswith(('https://','http://','#')):
            continue
        path = HERE/unquote(target.split('#')[0])
        assert path.exists(), f'Broken local link: {target}'
        checked.append(target)
    report = {'state':'pass','publicationState':'complete' if args.final else 'prepared','localJpgEpisodes':len(episodes),'projectAssets':len(assets),'projectBytes':sum(x['bytes'] for x in assets),'copiedFiles':len(copied),'copiedBytes':sum(x['bytes'] for x in copied),'readmeRelativeLinksChecked':checked,'readmeSha256':sha(HERE/'README.md'),'note':'No upload/publish/commit actions; source copies preserve bytes; remote visibility is separate.'}
    write_json(HERE/'manifests/docs-validation.json', report)
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
