"""Check native image dimensions locally using the shared gdocs header reader.

No network, credentials or document operations. Exits 1 if any file fails.
Square images require visual review because Khanh specified no square minimum.
"""

import argparse
import importlib.util
import json
import struct
from pathlib import Path


DEFAULT_HELPER = Path(r'E:\.trueprofit-claude-codex\shared\tools\gdocs\gdocs.py')


def inspect(path, image_size):
    result = {'file': str(path), 'ok': False}
    try:
        byte_count = path.stat().st_size
        if byte_count >= 50 * 1024 * 1024:
            raise ValueError('File must be under 50 MB for Google Docs')
        data = path.read_bytes()
        (width, height), fmt = image_size(data)
        result.update(width=width, height=height, format=fmt, bytes=byte_count)
        if width <= 0 or height <= 0:
            raise ValueError('Invalid image dimensions')
        if width * height > 25_000_000:
            raise ValueError('Image exceeds the 25-megapixel Google Docs limit')
        if width > height:
            result['orientation'] = 'horizontal'
            if width < 800:
                raise ValueError('Horizontal source must be at least 800 pixels wide')
        elif height > width:
            result['orientation'] = 'vertical'
            if height < 600:
                raise ValueError('Vertical source must be at least 600 pixels tall')
        else:
            result['orientation'] = 'square'
            result['review'] = 'No separate square minimum specified; review original quality and readability'
        result['ok'] = True
    except (OSError, ValueError, SystemExit, IndexError, struct.error) as exc:
        result['error'] = str(exc)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('images', nargs='+', type=Path)
    parser.add_argument('--helper', type=Path, default=DEFAULT_HELPER)
    parser.add_argument('--out', type=Path, help='Optional JSON report; does not modify images')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('gdocs_image_headers', args.helper)
    if spec is None or spec.loader is None:
        parser.error('Cannot load the shared gdocs helper')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    results = [inspect(path, helper.image_size) for path in args.images]
    report = {'all_ok': all(item['ok'] for item in results), 'images': results,
              'note': 'Header checks only; inspect every actual image and verify source provenance.'}
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(output + '\n', encoding='utf-8')
    print(output)
    return 0 if report['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
