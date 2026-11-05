import json,time
from pathlib import Path
OUT=Path(__file__).parent
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
jpg=read('jpg-independent-summary.json');remote=read('remote-independent-audit.json');runtime=read('ccproj-runtime-audit.json');zips=read('new-projects-zip-content-audit.json');configs=read('snapshot-config-fields-audit.json');coverage=read('outputs-independent-coverage-audit.json');supplement=read('supplement-independent-source-audit.json');sealed=read('s1-sealed-video-identity.json')
checks={
 'all_24_jpg_archives_independently_verified':jpg['pass'] and jpg['complete']==24 and jpg['jpgEntries']==2061018 and jpg['regularJpg']==823577 and jpg['hardlinkJpg']==1237441,
 'all_ready_assets_remote_digest_and_size_match':remote['state']=='PASS',
 'all_5579_output_paths_and_bytes_covered':coverage['pass'] and coverage['expectedOutputFiles']==5579,
 'nonsecret_filter_supplement_169_source_files_match':supplement['pass'] and supplement['expectedUniqueSourcePaths']==169,
 'seven_ccproj_runtime_bytes_and_sha_match_no_credentials':runtime['ccprojCount']==7 and runtime['highConfidenceSecretCount']==0 and runtime['sensitiveFilenameCount']==0 and all(r['startHashMatches'] and r['endHashMatches'] and r['startBytesMatch'] for r in runtime['projects']),
 'all_new_zip_code_and_config_secret_scan_pass':zips['sensitiveCandidateCount']==0 and zips['credentialPatternCount']==0,
 'snapshot_configs_have_no_unreviewed_secret_values':all(f['classification']!='review-nonempty-string' for r in configs for f in r['fields']),
 's1_four_rounds_and_canonical_video_sha_unchanged':sealed['pass'],
}
public=remote.get('requirePublic') and all(x.get('success') for x in remote.get('anonymousPublicChecks',{}).values()) and len(remote.get('anonymousPublicChecks',{}))==2 and not any(remote['remoteDrafts'].values())
result={'state':('PUBLIC_PASS' if public else 'PREPUBLIC_CHECKS_PASS') if all(checks.values()) else 'PENDING_OR_FAILED','checkedUnix':time.time(),'checks':checks,'readyAssets':remote['readyAssets'],'jpgArchiveCount':jpg['complete'],'remotePublicVerified':bool(public),'sourceCoordinateFilesNote':'Initial mode=ro SQLite reads may have created zero-byte WAL and 32768-byte SHM files. No SQL mutation was performed; all subsequent reads immutable=1; all 24 WAL files observed zero bytes. Preserved dataset counts, JSONL SHA and sealed video SHA checked.','scopeLimits':['All 2061018 archived JPEG paths checked; all 823577 regular JPEG byte SHA checked. Only 12 reproducible JPEG decode samples per archive repeated, because original extraction already decoded all native JPEGs.','One full episode actually restored: 86102 JPG paths, hardlink identity and independent-copy SHA checked. Other episodes validated as full archive entry/byte graphs.','Independent output coverage checks all 5579 paths/bytes plus 80 fixed small-file SHA samples; publisher separately verified all source SHA.']}
(OUT/'independent-publication-gate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
