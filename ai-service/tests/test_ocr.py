"""
Manual OCR verification smoke test.

Usage:
  python tests/test_ocr.py

Uses a generated sample ID-style image with drawn text if no real sample
exists at tests/samples/id_document.jpg.
"""

import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.ocrService import assess_document_ocr


def make_sample_id_image():
    image = np.ones((420, 700, 3), dtype=np.uint8) * 245
    cv2.rectangle(image, (20, 20), (680, 400), (30, 30, 30), 2)

    lines = [
        (40, 70, 'REPUBLIC OF KENYA'),
        (40, 130, 'JOHN KAMAU MWANGI'),
        (40, 190, 'ID NO 12345678'),
        (40, 250, '01/01/1990'),
    ]

    for x, y, text in lines:
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (10, 10, 10),
            2,
            cv2.LINE_AA,
        )

    return image


if __name__ == '__main__':
    samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
    sample_path = os.path.join(samples_dir, 'id_document.jpg')

    if os.path.exists(sample_path):
        image = cv2.imread(sample_path)
        print(f'Loaded sample identity document from {sample_path}')
    else:
        image = make_sample_id_image()
        print('Using generated sample identity document image')

    registered = {
        'name': 'John Kamau Mwangi',
        'idNumber': '12345678',
        'dateOfBirth': '01/01/1990',
    }

    result = assess_document_ocr(image, registered)

    print('\n=== OCR Result ===')
    print(f"extractedName:      {result.get('extractedName')}")
    print(f"extractedIDNumber:  {result.get('extractedIDNumber')}")
    print(f"extractedDOB:       {result.get('extractedDOB')}")
    print(f"nameMatch:          {result.get('nameMatch')}")
    print(f"idMatch:            {result.get('idMatch')}")
    print(f"dobMatch:           {result.get('dobMatch')}")
    print(f"confidenceScore:    {result.get('confidenceScore')}")
    print(f"matched:            {result.get('matched')}")
    print(f"rawText:            {result.get('rawText')}")
