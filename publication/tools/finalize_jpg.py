import argparse, hashlib, json, pathlib, time
from pack_jpg import write_json, sha_file

HERE=pathlib.Path(__file__).resolve().parent

def finalize():
    episodes=[]
    for n in range(1,25):
        ep=f'S1E{n:02d}';path=HERE/f'{ep}.verified.json'
        if not path.exists():return False
        r=json.loads(path.read_text(encoding='utf-8'))
        if r.get('state')!='pass':return False
        archive=HERE/r['archive']
        if not archive.exists() or archive.stat().st_size!=r['archiveBytes'] or r['archiveBytes']>=2*1024**3:raise ValueError(f'Invalid archive size {ep}')
        if r['jpgPaths']!=r['regularJpegs']+r['hardlinkJpegs'] or r['regularJpegs']!=r['sourceFrameIds']:raise ValueError('Inconsistent counts')
        episodes.append(r)
    total=sum(x['jpgPaths'] for x in episodes);native=sum(x['sourceFrameIds'] for x in episodes);links=sum(x['hardlinkJpegs'] for x in episodes)
    if (total,native,links)!=(2061018,823577,1237441):raise ValueError(f'Unexpected totals {(total,native,links)}')
    manifest={'formatVersion':1,'state':'pass','scope':'24 complete 640x360/q6 JPEG sample-path archives; 60-Hz sampling, repeated paths preserved as tar hardlinks; not interpolated frames','episodesCount':24,'jpgPaths':total,'sourceFrameIds':native,'regularJpegs':native,'hardlinkJpegs':links,'archiveBytes':sum(x['archiveBytes'] for x in episodes),'episodes':episodes,'generatedUnix':time.time()}
    write_json(HERE/'jpg-manifest.json',manifest)
    (HERE/'SHA256SUMS-JPG.txt').write_text(''.join(f"{r['archiveSha256']}  {r['archive']}\n" for r in episodes),encoding='ascii')
    (HERE/'JPG-ARCHIVES.csv').write_text('episode,archive,bytes,sha256,jpg_paths,regular_jpegs,hardlink_jpegs\n'+''.join(f"{r['id']},{r['archive']},{r['archiveBytes']},{r['archiveSha256']},{r['jpgPaths']},{r['regularJpegs']},{r['hardlinkJpegs']}\n" for r in episodes),encoding='ascii')
    ready=HERE/'ready';ready.mkdir(exist_ok=True)
    for name in ('jpg-manifest.json','SHA256SUMS-JPG.txt','JPG-ARCHIVES.csv','restore_jpg.py','pack_jpg.py','README_JPG.zh-CN.md'):
        path=HERE/name
        write_json(ready/f'{name}.json',{'state':'verified','path':str(path.resolve()),'name':name,'bytes':path.stat().st_size,'sha256':sha_file(path),'release':'jpg','jpgPaths':0})
    print(f'PASS {total} JPG paths; {native} native source frame IDs; {links} hardlinks; {manifest["archiveBytes"]} archive bytes',flush=True)
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--wait',action='store_true');a=p.parse_args()
    while not finalize():
        if not a.wait:raise SystemExit('Not all 24 episode archives have verified reports yet')
        time.sleep(15)
