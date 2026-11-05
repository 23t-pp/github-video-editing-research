"""Read-only public documentation audit; writes its report inside publication/ only."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=HERE.parents[2])
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    staging = workspace/'work/publish-all-20261105'
    readme = (HERE/'README.md').read_text(encoding='utf-8')
    copy_manifest = json.loads((HERE/'manifests/copy-integrity.json').read_text(encoding='utf-8'))
    copied = copy_manifest['files']
    for item in copied:
        source, destination = workspace/item['source'], HERE/item['path']
        if not source.is_file() or not destination.is_file():
            raise ValueError('Missing original/copied source: '+item['path'])
        if source.stat().st_size != item['bytes'] or destination.stat().st_size != item['bytes'] or digest(source) != item['sha256'] or digest(destination) != item['sha256']:
            raise ValueError('Byte-preserved copy changed: '+item['path'])
    links = re.findall(r'\]\(([^)]+)\)', readme)
    local = []
    downloads = []
    for target in links:
        if target.startswith('#'):
            continue
        if not target.startswith(('http://', 'https://')):
            target_path = HERE/unquote(target.split('#')[0])
            if not target_path.exists():
                raise ValueError('Missing README target: '+target)
            local.append(target)
        elif '/releases/download/' in target:
            downloads.append(unquote(urlparse(target).path.rsplit('/',1)[1]))
    assets = json.loads((staging/'projects/assets-manifest.json').read_text(encoding='utf-8'))
    project_names = {a['asset'] for a in assets}
    published_project_links = set(downloads)-{f'S1E{n:02d}.tar.gz' for n in range(1,25)}-{'jjk-s1-final-60s.mp4','publication-audit-evidence.zip'}
    if published_project_links != project_names:
        raise ValueError('Download table project asset set mismatch')
    for asset in assets:
        marker = json.loads((staging/'projects/ready'/f"{asset['asset']}.json").read_text(encoding='utf-8'))
        if marker['bytes'] != asset['bytes'] or marker['sha256'] != asset['sha256']:
            raise ValueError('Ready marker mismatch: '+asset['asset'])
        for external in asset.get('restore',{}).get('external_assets',[]):
            if 'asset' in external and external['asset'] not in project_names:
                raise ValueError('External HF/OCC missing from table: '+external['asset'])
    expected_jpg = {f'S1E{n:02d}.tar.gz' for n in range(1,25)}
    if expected_jpg-set(downloads):
        raise ValueError('24 episode expected download table is incomplete')
    required_commands = (
        'python -X utf8 ./restore_projects.py --downloads . --workspace D:/video-backup/workspace --with-sources',
        'python -X utf8 ./restore_jpg.py . --destination D:/video-backup/workspace/outputs/jjk-s1-workflow/素材集_60Hz_JPG --manifest ./jpg-manifest.json',
    )
    if any(x not in readme for x in required_commands):
        raise ValueError('Required restore command changed')
    evidence_marker = staging/'uploads/ready/publication-audit-evidence.zip.json'
    if evidence_marker.exists():
        item = json.loads(evidence_marker.read_text(encoding='utf-8'))
        remote = json.loads((HERE/'manifests/remote-assets-snapshot.json').read_text(encoding='utf-8'))
        found = next(x for x in remote['assets'] if x['name'] == item['name'])
        if found['remoteSize'] != item['bytes'] or found['remoteDigest'] != 'sha256:'+item['sha256']:
            raise ValueError('Audit evidence download marker mismatch')
    root_readme = HERE.parent/'README.md'
    root_text = root_readme.read_text(encoding='utf-8')
    root_local = []
    if root_text.startswith('# 全部剪辑工程、成片与2,061,018个JPG采样路径'):
        for target in re.findall(r'\]\(([^)]+)\)', root_text):
            if target.startswith(('http://','https://','#')):
                continue
            if not (HERE.parent/unquote(target.split('#')[0])).exists():
                raise ValueError('Missing root README target: '+target)
            root_local.append(target)
    report = {
        'state':'pass', 'scope':'Independent static audit of generated publication hub, source-copy integrity and ready asset names; does not claim remote public visibility',
        'projectAssetNamesChecked':len(project_names), 'jpgExpectedNamesChecked':len(expected_jpg),
        'readmeLocalLinksChecked':local, 'sourceCopiesVerified':len(copied),
        'sourceCopyBytesVerified':sum(x['bytes'] for x in copied),
        'readmeSha256':digest(HERE/'README.md'),
        'rootReadmeSha256':digest(root_readme) if root_local else None,
        'rootReadmeLocalLinksChecked':root_local,
        'restoreCommands':'Project --downloads/--workspace/--with-sources and JPG --destination/--manifest match script argparse; --help checked in preparing session',
    }
    path = HERE/'manifests/static-docs-audit.json'
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
