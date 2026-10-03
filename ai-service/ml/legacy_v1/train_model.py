"""
Module 12 — Production retraining script for the SVM KYC classifier.

Runs the pipeline from notebooks/02_model_training.ipynb non-interactively:
load -> stratified 70/15/15 split -> MinMaxScaler -> SVM (tuned C/gamma) ->
test-set evaluation -> save model, scaler, evaluation report and version file.

Usage (from the ai-service directory):
    python ml/train_model.py                  # bumps the patch version (1.0.0 -> 1.0.1)
    python ml/train_model.py --version 2.0.0  # sets an explicit version
"""

import argparse
import json
import os
import re
import warnings
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_recall_fscore_support)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.svm import SVC

# scikit-learn >= 1.9 deprecates SVC(probability=True); the API still needs predict_proba
warnings.filterwarnings('ignore', message='.*probability.*', category=FutureWarning)

ML_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ML_DIR, 'data', 'synthetic_verification_dataset.csv')
MODEL_DIR = os.path.join(ML_DIR, 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'svm_kyc_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
VERSION_PATH = os.path.join(MODEL_DIR, 'model_version.txt')
REPORT_PATH = os.path.join(ML_DIR, 'reports', 'evaluation_report.json')

RANDOM_STATE = 42
FEATURES = ['faceMatchScore', 'livenessScore', 'ocrConfidenceScore',
            'blurScore', 'brightnessScore', 'contrastScore']
CLASS_KEYS = ['verified', 'review', 'rejected']  # label 0, 1, 2
CLASS_NAMES = ['Verified', 'Manual Review', 'Rejected']

# Selected by GridSearchCV (5-fold stratified, f1_macro) in 02_model_training.ipynb
BEST_C = 0.1
BEST_GAMMA = 0.1


def load_and_split():
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURES].values
    y = LabelEncoder().fit_transform(df['label'].values)

    X_train, X_hold, y_train, y_hold = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE)
    X_val, X_test, y_val, y_test = train_test_split(
        X_hold, y_hold, test_size=0.50, stratify=y_hold, random_state=RANDOM_STATE)
    return df, (X_train, y_train), (X_val, y_val), (X_test, y_test)


def read_current_version():
    try:
        with open(VERSION_PATH, encoding='utf-8') as handle:
            match = re.search(r'(\d+)\.(\d+)\.(\d+)', handle.readline())
            return tuple(int(part) for part in match.groups()) if match else None
    except FileNotFoundError:
        return None


def next_version(explicit=None):
    if explicit:
        return explicit
    current = read_current_version()
    if current is None:
        return '1.0.0'
    major, minor, patch = current
    return f'{major}.{minor}.{patch + 1}'


def write_version_file(version, trained_at):
    with open(VERSION_PATH, 'w', encoding='utf-8') as handle:
        handle.write(f'{version}\n')
        handle.write(f'trained_at={trained_at}\n')


def build_report(y_test, y_pred, version, trained_at, dataset_size, split_sizes):
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=[0, 1, 2], zero_division=0)
    per_class = {
        key: {
            'label': name,
            'precision': round(float(precision[i]), 4),
            'recall': round(float(recall[i]), 4),
            'f1': round(float(f1[i]), 4),
            'support': int(support[i]),
        }
        for i, (key, name) in enumerate(zip(CLASS_KEYS, CLASS_NAMES))
    }
    return {
        'model_version': version,
        'training_date': trained_at,
        'dataset_size': dataset_size,
        'split_sizes': split_sizes,
        'accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
        'macro_f1': round(float(f1_score(y_test, y_pred, average='macro')), 4),
        'weighted_f1': round(float(f1_score(y_test, y_pred, average='weighted')), 4),
        'per_class': per_class,
        'confusion_matrix': confusion_matrix(y_test, y_pred, labels=[0, 1, 2]).tolist(),
        'confusion_matrix_labels': CLASS_KEYS,
        'best_params': {'C': BEST_C, 'gamma': BEST_GAMMA},
        'kernel': 'rbf',
        'features': FEATURES,
    }


def main():
    parser = argparse.ArgumentParser(description='Retrain the SVM KYC classifier')
    parser.add_argument('--version', help='explicit version string (default: bump patch)')
    args = parser.parse_args()

    df, (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_and_split()
    print(f'Loaded {len(df)} records: train={len(y_train)} val={len(y_val)} test={len(y_test)}')

    scaler = MinMaxScaler(clip=True)
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    model = SVC(
        kernel='rbf',
        C=BEST_C,
        gamma=BEST_GAMMA,
        class_weight='balanced',
        probability=True,
        random_state=RANDOM_STATE,
    )
    model.fit(X_train_s, y_train)
    print(f'Trained SVC(kernel=rbf, C={BEST_C}, gamma={BEST_GAMMA}, class_weight=balanced)')

    val_f1 = f1_score(y_val, model.predict(X_val_s), average='macro')
    print(f'Validation macro F1: {val_f1:.4f}')

    y_pred = model.predict(X_test_s)
    print('\nTest set classification report:')
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES, digits=4))

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    version = next_version(args.version)
    trained_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    write_version_file(version, trained_at)

    report = build_report(
        y_test, y_pred, version, trained_at,
        dataset_size=len(df),
        split_sizes={'train': len(y_train), 'validation': len(y_val), 'test': len(y_test)},
    )
    with open(REPORT_PATH, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)

    print(f'Saved model   -> {MODEL_PATH}')
    print(f'Saved scaler  -> {SCALER_PATH}')
    print(f'Saved report  -> {REPORT_PATH}')
    print(f'Model version -> {version} ({trained_at})')


if __name__ == '__main__':
    main()
