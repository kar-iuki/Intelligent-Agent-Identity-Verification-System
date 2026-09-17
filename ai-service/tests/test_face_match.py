"""
Manual face-match smoke test.

Usage:
  python tests/test_face_match.py

Place optional sample images under tests/samples/:
  same_person_1.jpg, same_person_2.jpg
  different_person_1.jpg, different_person_2.jpg

If samples are missing, synthetic face-like placeholders are used so the
script still exercises the API (scores will not be meaningful).
"""

import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.faceMatchService import face_app, model_init_error, verify_face_match


def make_placeholder(seed=0, size=256):
    rng = np.random.default_rng(seed)
    image = np.full((size, size, 3), 180, dtype=np.uint8)
    # Rough oval "face" region so detectors have something to look at
    center = (size // 2, size // 2)
    axes = (size // 3, size // 2 - 20)
    color = tuple(int(c) for c in rng.integers(40, 120, size=3))
    cv2.ellipse(image, center, axes, 0, 0, 360, color, -1)
    cv2.circle(image, (size // 2 - 35, size // 2 - 20), 10, (20, 20, 20), -1)
    cv2.circle(image, (size // 2 + 35, size // 2 - 20), 10, (20, 20, 20), -1)
    cv2.ellipse(image, (size // 2, size // 2 + 40), (30, 15), 0, 0, 180, (20, 20, 20), 2)
    return image


def load_or_placeholder(path, seed):
    if os.path.exists(path):
        image = cv2.imread(path)
        print(f'Loaded {path}')
        return image
    print(f'Missing {path} — using placeholder (seed={seed})')
    return make_placeholder(seed=seed)


if __name__ == '__main__':
    if face_app is None:
        print('InsightFace model failed to initialise:')
        print(model_init_error)
        sys.exit(1)

    samples = os.path.join(os.path.dirname(__file__), 'samples')
    same_1 = load_or_placeholder(os.path.join(samples, 'same_person_1.jpg'), 1)
    same_2 = load_or_placeholder(os.path.join(samples, 'same_person_2.jpg'), 1)
    diff_1 = load_or_placeholder(os.path.join(samples, 'different_person_1.jpg'), 2)
    diff_2 = load_or_placeholder(os.path.join(samples, 'different_person_2.jpg'), 3)

    same_result = verify_face_match(same_1, same_2)
    diff_result = verify_face_match(diff_1, diff_2)

    print('\n=== Same person pair ===')
    print(same_result)
    print('\n=== Different person pair ===')
    print(diff_result)

    print('\nExpected (with real photos): same-person > 70, different-person < 50')
