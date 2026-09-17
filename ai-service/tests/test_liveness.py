"""
Manual liveness detection smoke test.

Usage:
  python tests/test_liveness.py

Optional samples:
  tests/samples/real_face.jpg
  tests/samples/spoof_face.jpg
"""

import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.livenessService import assess_liveness, model_init_error, model_ready


def make_placeholder_face(seed=0, size=320):
    rng = np.random.default_rng(seed)
    image = np.full((size, int(size * 0.75), 3), 200, dtype=np.uint8)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    axes = (w // 3, h // 3)
    color = tuple(int(c) for c in rng.integers(60, 140, size=3))
    cv2.ellipse(image, center, axes, 0, 0, 360, color, -1)
    cv2.circle(image, (w // 2 - 25, h // 2 - 20), 8, (20, 20, 20), -1)
    cv2.circle(image, (w // 2 + 25, h // 2 - 20), 8, (20, 20, 20), -1)
    return image


def load_or_placeholder(path, seed):
    if os.path.exists(path):
        image = cv2.imread(path)
        print(f'Loaded {path}')
        return image
    print(f'Missing {path} — using placeholder (seed={seed})')
    return make_placeholder_face(seed=seed)


if __name__ == '__main__':
    if not model_ready:
        print('Silent-Face model failed to initialise:')
        print(model_init_error)
        sys.exit(1)

    samples = os.path.join(os.path.dirname(__file__), 'samples')
    real = load_or_placeholder(os.path.join(samples, 'real_face.jpg'), 1)
    spoof = load_or_placeholder(os.path.join(samples, 'spoof_face.jpg'), 2)

    print('\n=== Real face ===')
    print(assess_liveness(real))
    print('\n=== Spoof / print / screen ===')
    print(assess_liveness(spoof))
    print('\nExpected (with real samples): live > 0.75, spoof < 0.50')
