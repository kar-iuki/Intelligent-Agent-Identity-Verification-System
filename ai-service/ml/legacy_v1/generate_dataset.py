"""
Module 12 — Synthetic KYC verification dataset generator.

Feature distributions are parameterised from the empirical score ranges
documented in notebooks/01_distribution_analysis.ipynb:
  * faceMatchScore           — LFW / ArcFace verification literature
  * livenessScore            — NUAA and Replay-Attack anti-spoofing benchmarks
  * ocrConfidenceScore       — MIDV-500 identity document OCR
  * blur/brightness/contrast — MIDV-500 image quality analysis

Usage (from the ai-service directory):
    python ml/generate_dataset.py
"""

import os
import random

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

ML_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(ML_DIR, 'data', 'synthetic_verification_dataset.csv')

FEATURES = [
    'faceMatchScore',
    'livenessScore',
    'ocrConfidenceScore',
    'blurScore',
    'brightnessScore',
    'contrastScore',
]

LABELS = {'verified': 0, 'review': 1, 'rejected': 2}

RECORDS_PER_CLASS = {
    'verified': 2400,
    'review': 800,
    'rejected': 800,
}

# (mean, std, clip_low, clip_high) per feature per class
DISTRIBUTIONS = {
    'verified': {
        'faceMatchScore': (87.0, 5.0, 80.0, 100.0),
        'livenessScore': (0.88, 0.05, 0.75, 1.0),
        'ocrConfidenceScore': (0.82, 0.06, 0.70, 1.0),
        'blurScore': (150.0, 30.0, 80.0, 300.0),
        'brightnessScore': (140.0, 25.0, 80.0, 200.0),
        'contrastScore': (65.0, 12.0, 30.0, 100.0),
    },
    'review': {
        'faceMatchScore': (65.0, 8.0, 50.0, 80.0),
        'livenessScore': (0.62, 0.08, 0.50, 0.75),
        'ocrConfidenceScore': (0.55, 0.08, 0.40, 0.70),
        'blurScore': (65.0, 12.0, 40.0, 80.0),
        # Under-exposed branch; the over-exposed branch is handled separately below
        'brightnessScore': (55.0, 15.0, 20.0, 80.0),
        'contrastScore': (22.0, 5.0, 15.0, 30.0),
    },
    'rejected': {
        'faceMatchScore': (35.0, 10.0, 0.0, 50.0),
        'livenessScore': (0.30, 0.10, 0.0, 0.50),
        'ocrConfidenceScore': (0.25, 0.10, 0.0, 0.40),
        'blurScore': (30.0, 10.0, 0.0, 40.0),
        'brightnessScore': (20.0, 8.0, 0.0, 20.0),
        'contrastScore': (10.0, 4.0, 0.0, 15.0),
    },
}

# Manual Review brightness is bimodal: most borderline captures are too dark
# (20-80) but a minority are over-exposed (above 200, e.g. glare on the laminate).
REVIEW_OVEREXPOSED_SHARE = 0.20
REVIEW_OVEREXPOSED = (220.0, 12.0, 200.0, 255.0)

# Small Gaussian noise added after clipping so class boundaries are not
# perfectly clean — values sit roughly at 2% of each feature's natural range.
NOISE_STD = {
    'faceMatchScore': 2.0,
    'livenessScore': 0.02,
    'ocrConfidenceScore': 0.02,
    'blurScore': 5.0,
    'brightnessScore': 5.0,
    'contrastScore': 2.0,
}

# Physical bounds of each score as produced by the AI service
FEATURE_BOUNDS = {
    'faceMatchScore': (0.0, 100.0),
    'livenessScore': (0.0, 1.0),
    'ocrConfidenceScore': (0.0, 1.0),
    'blurScore': (0.0, None),
    'brightnessScore': (0.0, 255.0),
    'contrastScore': (0.0, None),
}


def sample_clipped_normal(mean, std, low, high, size):
    return np.clip(np.random.normal(mean, std, size), low, high)


def generate_class(label_name, n):
    columns = {}
    for feature in FEATURES:
        mean, std, low, high = DISTRIBUTIONS[label_name][feature]
        values = sample_clipped_normal(mean, std, low, high, n)

        if label_name == 'review' and feature == 'brightnessScore':
            overexposed = np.random.rand(n) < REVIEW_OVEREXPOSED_SHARE
            values[overexposed] = sample_clipped_normal(*REVIEW_OVEREXPOSED, overexposed.sum())

        values = values + np.random.normal(0.0, NOISE_STD[feature], n)
        lower, upper = FEATURE_BOUNDS[feature]
        columns[feature] = np.clip(values, lower, upper)

    frame = pd.DataFrame(columns)
    frame['label'] = LABELS[label_name]
    return frame


def generate_dataset():
    frames = [generate_class(name, n) for name, n in RECORDS_PER_CLASS.items()]
    dataset = pd.concat(frames, ignore_index=True)
    dataset = dataset.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    return dataset[FEATURES + ['label']].round(4)


def print_summary(dataset):
    names = {v: k for k, v in LABELS.items()}
    print(f'Dataset saved to {OUTPUT_PATH}')
    print(f'Total records: {len(dataset)}\n')

    print('Class distribution:')
    counts = dataset['label'].value_counts().sort_index()
    for label, count in counts.items():
        print(f'  {label} ({names[label]:<8}) {count:>5}  ({count / len(dataset):.0%})')

    print('\nFeature statistics (all classes):')
    print(dataset[FEATURES].describe().round(3).to_string())

    print('\nFeature means per class:')
    per_class = dataset.groupby('label')[FEATURES].mean().round(3)
    per_class.index = [names[i] for i in per_class.index]
    print(per_class.to_string())


if __name__ == '__main__':
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = generate_dataset()
    df.to_csv(OUTPUT_PATH, index=False)
    print_summary(df)
