"""Measure the nearest detected audio transients to native-frame visual events."""

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT = '12 17 21 24 28 32 36 48 60 72 76 80 84 88 92 96 108 143 151 168 180 184 188 191 204 210 214 218 223 226 230 234 237 239 247 252 261 266 317 318 369 393 438 451 455 459 463 467 471 474 491 495 511 518 522 536 541 546 549 557 572 586'
DETECTORS = ('any', 'wide', 'low', 'high')


def read_peaks(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row['time_seconds'] = float(row['time_seconds'])
        row['detectors'] = row['detectors'].split('+')
    return rows


def align(peaks, frames, fps, limit_frames):
    for frame in frames:
        time = frame / fps
        row = {'frame0': frame, 'pts_seconds': f'{time:.6f}'}
        for detector in DETECTORS:
            matches = [peak for peak in peaks if detector == 'any' or detector in peak['detectors']]
            nearest = min(matches, key=lambda peak: abs(peak['time_seconds'] - time), default=None)
            if nearest and abs(nearest['time_seconds'] - time) > limit_frames / fps:
                nearest = None
            if nearest is None:
                row.update({f'{detector}_peak_seconds': '', f'{detector}_delta_ms': '',
                            f'{detector}_delta_frames': '', f'{detector}_band_hz': '', f'{detector}_strength': ''})
                continue
            delay = nearest['time_seconds'] - time
            strength = nearest[f'{"wide" if detector == "any" else detector}_flux']
            row.update({f'{detector}_peak_seconds': f'{nearest["time_seconds"]:.6f}',
                        f'{detector}_delta_ms': f'{delay*1000:+.2f}', f'{detector}_delta_frames': f'{delay*fps:+.2f}',
                        f'{detector}_band_hz': nearest['dominant_band_hz'], f'{detector}_strength': strength})
        yield row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--onsets', type=Path, default=ROOT / 'mix-onsets.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'cue-alignment.csv')
    parser.add_argument('--frames', default=DEFAULT, help='Zero-based frame indexes, comma- or space-separated')
    parser.add_argument('--fps', type=float, default=30)
    parser.add_argument('--limit-frames', type=float, default=1.5)
    args = parser.parse_args()
    frames = [int(f) for f in re.split(r'[,\s]+', args.frames.strip())]
    rows = list(align(read_peaks(args.onsets), frames, args.fps, args.limit_frames))
    with args.output.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row['frame0'], row['pts_seconds'], *(row[f'{detector}_delta_ms'] or '-' for detector in DETECTORS))


if __name__ == '__main__':
    main()
