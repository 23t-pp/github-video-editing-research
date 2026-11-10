"""Export the 30 CFR V21 source on its requested 60 Hz review grid."""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    library = Path(__file__).resolve().parents[1]
    analysis = library / 'data/frame-analysis'
    evidence = library / 'evidence/V21'
    samples = evidence / 'samples-60hz'
    native = json.loads((analysis / 'V21-pts.json').read_text(encoding='utf-8'))
    source_report = json.loads((analysis / 'V21.json').read_text(encoding='utf-8'))
    with args.source.open('rb') as source:
        source_sha = hashlib.file_digest(source, 'sha256').hexdigest()
    if source_sha != source_report['sourceSha256']:
        raise ValueError('Source SHA differs from the native analysis')
    if source_report['fps'] != '30/1' or len(native) != 928:
        raise ValueError('Expected the original 30 CFR V21 with 928 native frames')
    if any(row['i'] != i or abs(row['pts'] - i / 30) > 0.000001
           for i, row in enumerate(native)):
        raise ValueError('Native PTS diverges from the 30 CFR mapping')
    with (analysis / 'V21.csv').open(encoding='utf-8', newline='') as source:
        metrics = list(csv.DictReader(source))
    if len(metrics) != len(native):
        raise ValueError('Native metric and PTS counts differ')

    jpeg_stream = subprocess.run([
        os.environ.get('FFMPEG_PATH', 'ffmpeg'), '-v', 'error', '-nostdin',
        '-i', str(args.source), '-map', '0:v:0', '-an', '-fps_mode', 'passthrough',
        '-c:v', 'mjpeg', '-q:v', '3', '-threads', '2', '-f', 'image2pipe', 'pipe:1',
    ], check=True, capture_output=True).stdout
    jpegs = []
    offset = 0
    while offset < len(jpeg_stream):
        end = jpeg_stream.find(b'\xff\xd9', offset + 2)
        if jpeg_stream[offset:offset + 2] != b'\xff\xd8' or end < 0:
            raise ValueError(f'Invalid JPEG at byte {offset}')
        jpegs.append(jpeg_stream[offset:end + 2])
        offset = end + 2
    if len(jpegs) != len(native):
        raise ValueError(f'Decoded {len(jpegs)} JPEGs for {len(native)} timestamps')

    samples.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 12)
    rows, pages = [], []
    count = len(native) * 2
    sheet = None
    for source_index, jpeg in enumerate(jpegs):
        digest = hashlib.sha256(jpeg).hexdigest()
        first = source_index * 2
        first_path = samples / f'S{first:07d}.jpg'
        if first_path.exists():
            if hashlib.sha256(first_path.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Existing JPEG differs: {first_path.name}')
        else:
            first_path.write_bytes(jpeg)
        with Image.open(io.BytesIO(jpeg)) as decoded:
            if decoded.size != (1620, 1080):
                raise ValueError(f'Unexpected dimensions: {decoded.size}')
            thumb = ImageOps.contain(decoded, (160, 90), Image.Resampling.LANCZOS)
        for sample in (first, first + 1):
            file = samples / f'S{sample:07d}.jpg'
            if sample != first and not file.exists():
                os.link(first_path, file)
            if not file.samefile(first_path):
                raise ValueError(f'Expected a hardlink: {file.name}')
            rows.append({
                'sample': sample, 'sample_time_sec': f'{sample / 60:.9f}',
                'native_frame': source_index, 'source_pts_sec': f'{native[source_index]["pts"]:.6f}',
                'repeated_source_frame': int(sample != first), 'native_first_sample': first,
                'rgb_mad_0to1': metrics[source_index]['rgb_mad_0to1'] if sample == first else '0',
                'luma_0to255': metrics[source_index]['luma_0to255'],
                'jpg_path': file.relative_to(library).as_posix(), 'jpg_sha256': digest,
            })
            slot = sample % 60
            if slot == 0:
                sheet = Image.new('RGB', (1642, 674), '#1c1c1c')
            x, y = (slot % 10) * 164 + 2, (slot // 10) * 112 + 2
            sheet.paste(thumb, (x + (160 - thumb.width) // 2, y))
            draw = ImageDraw.Draw(sheet)
            flag = '=' if sample != first else ' '
            draw.text((x + 1, y + 91), f'S{sample:04d} N{source_index:03d}{flag} {sample / 60:06.3f}s',
                      font=font, fill='#ebc377' if flag == '=' else '#f3f3f3')
            if slot == 59 or sample == count - 1:
                name = f'60hz-{sample // 60 + 1:03d}.jpg'
                sheet.save(evidence / name, quality=91, subsampling=0)
                pages.append({'file': name, 'firstFrame': sample - slot, 'lastFrame': sample,
                              'start': round((sample - slot) / 60, 6),
                              'end': round(sample / 60, 6), 'count': slot + 1})

    if len(list(samples.glob('*.jpg'))) != count or len(rows) != count:
        raise ValueError('Sample path count does not match the 60 Hz grid')
    mapping = analysis / 'V21-60hz.csv'
    with mapping.open('w', encoding='utf-8', newline='') as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {
        'id': 'V21', 'sourceSha256': source_sha, 'sampleRate': 60, 'sampleCount': count,
        'nativeFrameRate': '30/1', 'nativeFrameCount': len(native),
        'regularJpegCount': len(native), 'repeatedSampleCount': len(native),
        'sampleDimensions': [1620, 1080], 'videoEndExclusiveSec': count / 60,
        'mappingRule': 'S at S/60 seconds maps to native N=floor(S/2), with observed source PTS.',
        'interpolation': False, 'repeatStorage': 'NTFS hardlink to the previous 60 Hz sample',
        'sampleDirectory': samples.relative_to(library).as_posix(),
        'mappingCsv': mapping.relative_to(library).as_posix(), 'pages': pages,
    }
    (analysis / 'V21-60hz.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'id': 'V21', 'samplePaths': count, 'nativeJpegs': len(native),
                      'aliasPaths': len(native), 'atlasPages': len(pages), 'sourceSha256': source_sha}))


if __name__ == '__main__':
    main()
