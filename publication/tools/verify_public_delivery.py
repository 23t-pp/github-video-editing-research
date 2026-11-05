"""Anonymous HTTP checks after publication; no credentials or signed redirects saved."""
import argparse
import hashlib
import json
import subprocess
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = '23t-pp/github-video-editing-research'


def request(url, limit=None, headers=None):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'public-delivery-verification', **(headers or {})})
            with urllib.request.urlopen(req, timeout=45) as response:
                body = response.read() if limit is None else response.read(limit)
                return body, {'requestedUrl': url, 'status': response.status,
                              'contentRange': response.headers.get('Content-Range'),
                              'returnedBytes': len(body)}
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    actions = json.loads((HERE/'publish-actions.json').read_text(encoding='utf-8'))
    report = {'expectedSourceCommit': args.commit, 'checkedUnix': time.time(),
              'anonymousReleaseChecks': {}, 'anonymousDownloads': []}
    for kind, record in actions.items():
        body, response = request(f'https://api.github.com/repos/{REPO}/releases/tags/{record["tag"]}')
        release = json.loads(body)
        assert not release['draft'] and release['published_at'] and release['id'] == record['releaseId']
        assert len(release['assets']) == record['assets']
        report['anonymousReleaseChecks'][kind] = {**response, 'assets': len(release['assets']), 'draft': False}
    refs = subprocess.check_output(['git', 'ls-remote', f'https://github.com/{REPO}.git',
                                    'refs/heads/main', *['refs/tags/'+r['tag'] for r in actions.values()]],
                                   text=True, encoding='utf-8')
    ref_map = dict((line.split()[1], line.split()[0]) for line in refs.splitlines())
    assert ref_map['refs/heads/main'] == args.commit
    for record in actions.values():
        assert ref_map['refs/tags/'+record['tag']] == args.commit
    report['gitRefs'] = ref_map
    local_readme = (ROOT/'outputs/github-video-editing-research/README.md').read_bytes()
    readme, response = request(f'https://raw.githubusercontent.com/{REPO}/{args.commit}/README.md')
    assert readme == local_readme
    report['anonymousReadme'] = {**response, 'sha256': hashlib.sha256(readme).hexdigest(), 'matchesLocal': True}
    # Small, uncached data ranges prove anonymous access to real binary payloads.
    uploaded = json.loads((HERE/'remote-uploads.json').read_text(encoding='utf-8'))['results']
    for key in ['jpg/S1E01.tar.gz', 'jpg/S1E24.tar.gz', 'jpg/jpg-manifest.json',
                'projects/jjk-s1-final-60s.mp4', 'projects/publication-audit-evidence.zip']:
        record = uploaded[key]
        body, response = request(record['browserDownloadUrl'], 64, {'Range': 'bytes=0-63'})
        with Path(record['path']).open('rb') as source:
            assert body == source.read(64)
        report['anonymousDownloads'].append({**response, 'name': record['name'],
                                             'first64BytesSha256': hashlib.sha256(body).hexdigest(),
                                             'matchesLocal': True})
    report['state'] = 'PASS'
    (HERE/'public-delivery-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'state': report['state'], 'anonymousReleases': len(report['anonymousReleaseChecks']),
                      'anonymousBinaryDownloads': len(report['anonymousDownloads']), 'gitRefs': ref_map}, ensure_ascii=False))


if __name__ == '__main__':
    main()
