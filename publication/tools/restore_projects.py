"""Restore published editing projects without changing an existing different file."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,stat,tempfile,zipfile
from pathlib import Path,PurePosixPath

META='PUBLICATION-ASSET-RESTORE.json'

def disk_path(path:Path)->Path:
    value=str(path)
    if os.name!='nt' or value.startswith('\\\\?\\'):return path
    if value.startswith('\\\\'):return Path('\\\\?\\UNC\\'+value[2:])
    return Path('\\\\?\\'+value)

def logical_path(path:Path)->Path:
    value=str(path)
    if value.startswith('\\\\?\\UNC\\'):value='\\\\'+value[8:]
    elif value.startswith('\\\\?\\'):value=value[4:]
    return Path(value)

def digest(path:Path)->str:
    with disk_path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def target_path(root:Path,name:str)->Path:
    # ZIP uses '/', but reject Windows path tricks on every platform.
    if not name or '\\' in name or ':' in name:raise ValueError(f'不安全的归档路径: {name!r}')
    pp=PurePosixPath(name)
    if pp.is_absolute() or '..' in pp.parts:raise ValueError(f'路径越界: {name!r}')
    dest=logical_path(disk_path(root.joinpath(*pp.parts)).resolve())
    if not dest.is_relative_to(logical_path(root)):raise ValueError(f'路径越界或符号链接: {name!r}')
    return disk_path(dest)

def check_member(root:Path,entry:zipfile.ZipInfo)->Path:
    if stat.S_ISLNK(entry.external_attr>>16):raise ValueError(f'拒绝归档内符号链接: {entry.filename}')
    return target_path(root,entry.filename)

def safe_write(root:Path,name:str,source,expected_sha:str|None=None)->str:
    dest=target_path(root,name);dest.parent.mkdir(parents=True,exist_ok=True)
    # Stream into a sibling temporary file so CRC errors cannot leave half-written targets.
    fd,tmp=tempfile.mkstemp(prefix='.restore-',suffix='.tmp',dir=dest.parent);tmp=Path(tmp)
    try:
        h=hashlib.sha256()
        with os.fdopen(fd,'wb') as out:
            while chunk:=source.read(4*1024*1024):out.write(chunk);h.update(chunk)
        actual=h.hexdigest()
        if expected_sha and actual!=expected_sha:raise ValueError(f'SHA256不匹配: {name}')
        if dest.exists():
            if dest.is_file() and digest(dest)==actual:return 'same'
            raise FileExistsError(f'目标已有不同内容，未覆盖: {dest}')
        # Hard-link creation is atomic and refuses to overwrite a concurrent target.
        try:os.link(disk_path(tmp),disk_path(dest))
        except FileExistsError:
            if dest.is_file() and digest(dest)==actual:return 'same'
            raise FileExistsError(f'目标在恢复时出现不同内容，未覆盖: {dest}')
        return 'written'
    finally:tmp.unlink(missing_ok=True)

def build_plan(downloads:Path,root:Path,projects:list[str],with_sources:bool):
    packages=sorted(downloads.glob('*-complete.zip'))
    if projects:
        selected={p+'-complete.zip' for p in projects};packages=[p for p in packages if p.name in selected]
        missing=selected-{p.name for p in packages}
        if missing:raise FileNotFoundError('缺少工程完整包: '+', '.join(sorted(missing)))
    if not packages:raise FileNotFoundError(f'未找到*-complete.zip: {downloads}')
    if with_sources:
        for name in ('execution-and-research-sources.zip','openchatcut-app-source-snapshot.zip'):
            p=downloads/name
            if not p.exists():raise FileNotFoundError(f'缺少源码包: {p}')
            packages.append(p)
    supplement=downloads/'publication-supplement.zip'
    required_supplement=['jjk-s1-workflow']
    if supplement.exists():packages.append(supplement)
    elif any(p.name in {x+'-complete.zip' for x in required_supplement} for p in packages):raise FileNotFoundError('缺少publication-supplement.zip（包含非秘密素材指纹及侧脸证据补档）')
    copies=[];notices=[];seen={}
    for package in packages:
        with zipfile.ZipFile(package) as z:
            for entry in z.infolist():
                if entry.filename==META:continue
                check_member(root,entry)
            if META not in z.namelist():continue
            restore=json.loads(z.read(META))
            for external in restore.get('external_assets',[]):
                dest=external.get('restore_path');asset=external.get('asset')
                if not asset:
                    notices.append(f"独立JPG库（可选）: release {external.get('release','见JPG下载指南')} -> {dest}")
                    continue
                if Path(asset).name!=asset or '/' in asset or '\\' in asset:raise ValueError(f'不安全的资产名: {asset}')
                target_path(root,dest);source=downloads/asset
                if not source.is_file():raise FileNotFoundError(f'缺少独立工程资产: {source}；由{package.name}要求，放回目标{dest}')
                expected=external.get('sha256')
                if not expected:raise ValueError(f'独立工程资产缺少SHA256: {asset}')
                if digest(source)!=expected:raise ValueError(f'下载资产SHA256不匹配: {asset}')
                if dest in seen and seen[dest]!=expected:raise ValueError(f'多个包要求不同内容: {dest}')
                seen[dest]=expected;copies.append((source,dest,expected))
    # Verify whole downloaded assets when the release manifest is alongside them.
    mf=downloads/'assets-manifest.json'
    if mf.exists():
        raw=json.loads(mf.read_text(encoding='utf-8-sig'));items=raw if isinstance(raw,list) else raw.get('assets',[])
        hashes={x['asset']:x['sha256'] for x in items}
        for package in packages:
            if package.name in hashes and digest(package)!=hashes[package.name]:raise ValueError(f'完整包SHA256不匹配: {package.name}')
    return packages,copies,notices

def selected_entry(package:Path,name:str,projects:list[str])->bool:
    if package.name!='publication-supplement.zip' or not projects:return True
    parts=PurePosixPath(name).parts
    aliases={'reference-replay-next':'reference-replay-v07'}
    chosen=set(projects)|{aliases.get(x,x) for x in projects}
    return len(parts)>1 and parts[0] in ('outputs','work') and parts[1] in chosen

def restore(downloads:Path,root:Path,projects:list[str]|None=None,with_sources:bool=False)->dict:
    downloads=downloads.resolve();root=root.resolve()
    packages,copies,notices=build_plan(downloads,root,projects or [],with_sources)
    root.mkdir(parents=True,exist_ok=True);counts={'written':0,'same':0}
    for package in packages:
        print(f'解压核验: {package.name}',flush=True)
        with zipfile.ZipFile(package) as z:
            for entry in z.infolist():
                if entry.filename==META or not selected_entry(package,entry.filename,projects or []):continue
                dest=check_member(root,entry)
                if entry.is_dir():dest.mkdir(parents=True,exist_ok=True);continue
                with z.open(entry) as src:counts[safe_write(root,entry.filename,src)]+=1
    for source,name,expected in copies:
        print(f'回填独立工程: {source.name} -> {name}',flush=True)
        with source.open('rb') as src:counts[safe_write(root,name,src,expected)]+=1
    result={'state':'complete','workspace':str(root),'packages':[p.name for p in packages],**counts,'notices':sorted(set(notices))}
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True);return result

def main():
    p=argparse.ArgumentParser(description='安全还原完整剪辑工程（Python 3.11+，仅标准库）')
    p.add_argument('--downloads',type=Path,required=True,help='gh release download保存资产的目录')
    p.add_argument('--workspace',type=Path,required=True,help='新的还原工作区根目录')
    p.add_argument('--project',action='append',default=[],help='仅恢复指定项目，可重复；如jjk-s1-workflow')
    p.add_argument('--with-sources',action='store_true',help='同时解压执行源码和OpenChatCut app源码快照')
    a=p.parse_args()
    try:restore(a.downloads,a.workspace,a.project,a.with_sources)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:p.exit(1,f'恢复失败：{exc}\n已存在的不同内容不会被覆盖；修正缺档/路径后可重新运行。\n')
if __name__=='__main__':main()
