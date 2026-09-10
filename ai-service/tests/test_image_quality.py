"""
Manual threshold check for image quality assessment.

Usage:
  python tests/test_image_quality.py

Generates a sharp sample and a blurred sample in-memory so no external
image files are required.
"""

import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.imageQualityService import assess_image_quality


def make_clear_image(size=400):
    """High-contrast checkerboard — should pass quality checks."""
    image = np.zeros((size, size, 3), dtype=np.uint8)
    tile = 40
    for y in range(0, size, tile):
        for x in range(0, size, tile):
            if ((x // tile) + (y // tile)) % 2 == 0:
                image[y:y + tile, x:x + tile] = (220, 220, 220)
            else:
                image[y:y + tile, x:x + tile] = (40, 40, 40)
    return image


def make_blurry_image(size=400):
    """Heavily blurred mid-gray image — should fail blur/contrast."""
    clear = make_clear_image(size)
    return cv2.GaussianBlur(clear, (51, 51), 0)


def print_result(label, result):
    print(f'\n=== {label} ===')
    print(f"  blurScore:       {result['blurScore']}")
    print(f"  brightnessScore: {result['brightnessScore']}")
    print(f"  contrastScore:   {result['contrastScore']}")
    print(f"  passed:          {result['passed']}")
    print(f"  failures:        {result['failures']}")


if __name__ == '__main__':
    clear = make_clear_image()
    blurry = make_blurry_image()

    # Optional: also test files from tests/samples if present
    samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
    clear_path = os.path.join(samples_dir, 'clear.jpg')
    blurry_path = os.path.join(samples_dir, 'blurry.jpg')

    if os.path.exists(clear_path):
        clear = cv2.imread(clear_path)
        print(f'Loaded sample clear image from {clear_path}')
    else:
        print('Using generated clear sample image')

    if os.path.exists(blurry_path):
        blurry = cv2.imread(blurry_path)
        print(f'Loaded sample blurry image from {blurry_path}')
    else:
        print('Using generated blurry sample image')

    print_result('Clear image', assess_image_quality(clear))
    print_result('Blurry image', assess_image_quality(blurry))
