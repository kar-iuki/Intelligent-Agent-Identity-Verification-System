"""Train an offline LIBSVM candidate and compare it with the saved v3.1.0 baseline."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ML = HERE.parents[1]
sys.path.insert(0, str(ML.parent))
from ml.generate_dataset import generate_dataset
from ml.schema import FEATURES, CLASSES

# Independent draws. Development can be inspected before the final evaluation.
SEEDS = {'train': 120141, 'development': 120142, 'evaluation': 120143}
QUALITY = [[35, 110, 30], [80, 150, 45], [200, 185, 55]]
MODEL = 'candidate.model'
MODEL_VERSION = '3.1.1'


def draw(partition, counts):
    return generate_dataset(HERE / 'scenarios.json', seed=SEEDS[partition],
                            record_counts=dict(zip(CLASSES, counts)))[0]


def write_libsvm(path, frame, scaler):
    lo, hi = np.array(scaler['min']), np.array(scaler['max'])
    x = np.clip((frame[FEATURES].to_numpy() - lo) / (hi - lo), 0, 1)
    labels = frame.target.map(CLASSES.index) if 'target' in frame else np.zeros(len(x), dtype=int)
    with path.open('w') as handle:
        for label, row in zip(labels, x):
            fields = [f'{j}:{v:.17g}' for j, v in enumerate(row, 1)]
            print(label, *fields, file=handle)


def train(out, tmp):
    data, _ = generate_dataset(HERE / 'scenarios.json', seed=SEEDS['train'])
    scaler = {'model_version': MODEL_VERSION, 'features': FEATURES, 'classes': CLASSES, 'min': data[FEATURES].min().tolist(),
              'max': data[FEATURES].max().tolist()}
    (out / 'scaler.json').write_text(json.dumps(scaler, indent=2) + '\n')
    write_libsvm(tmp / 'train', data, scaler)
    # Same RBF C and gamma as 3.1.0. LIBSVM fits its probability model by internal CV.
    weights = []
    for i, name in enumerate(CLASSES):
        weights.extend([f'-w{i}', str(len(data) / (len(CLASSES) * (data.target == name).sum()))])
    subprocess.run(['svm-train', '-q', '-t', '2', '-c', '10', '-g', '1', '-b', '1',
                    *weights, tmp / 'train', out / MODEL], check=True)


def candidate_predict(frame, out, tmp):
    scaler = json.loads((out / 'scaler.json').read_text())
    write_libsvm(tmp / 'cases', frame, scaler)
    subprocess.run(['svm-predict', '-q', '-b', '1', tmp / 'cases', out / MODEL,
                    tmp / 'predictions'], check=True)
    pred = np.loadtxt(tmp / 'predictions', skiprows=1, ndmin=2)
    assert len(pred) == len(frame) and np.allclose(pred[:, 1:].sum(axis=1), 1, atol=2e-5)
    return np.asarray(CLASSES)[pred[:, 0].astype(int)]


def baseline_predict(frame):
    import joblib
    scaler = joblib.load(ML / 'models/scaler.pkl')
    model = joblib.load(ML / 'models/svm_kyc_model.pkl')
    return model.predict(scaler.transform(frame[FEATURES].to_numpy()))


def matrix(actual, predicted):
    counts = [[int(np.sum((actual == a) & (predicted == p))) for p in CLASSES] for a in CLASSES]
    cm = np.asarray(counts)
    return {'matrix': counts, 'accuracy': float(cm.trace() / cm.sum()),
            'macro_f1': float(np.mean(2 * cm.diagonal() / (cm.sum(axis=0) + cm.sum(axis=1))))}


def by_band(frame, predictions):
    face = frame.face_match_score.to_numpy()
    masks = [face < 25, (face >= 25) & (face <= 50), face > 50]
    return {band: {name: int(sum(predictions[mask] == name)) for name in CLASSES}
            for band, mask in zip(['below_25', '25_through_50', 'above_50'], masks)}


def probe():
    return pd.DataFrame([[face, 1, 1, *q] for q in QUALITY for face in range(101)], columns=FEATURES)


def evaluate(out, tmp, baseline=baseline_predict):
    manifest = json.loads((ML / 'models/artifact_manifest.json').read_text())
    if manifest['version'] != '3.1.0':
        raise ValueError('This comparison requires the original v3.1.0 baseline.')
    for filename in ['scaler.pkl', 'svm_kyc_model.pkl']:
        assert hashlib.sha256((ML / 'models' / filename).read_bytes()).hexdigest() == manifest['artifacts'][filename]
    fresh = draw('evaluation', [1800, 600, 600])
    original = pd.read_csv(ML / 'data/kyc_synthetic_dataset_10000.csv')
    split = pd.read_csv(ML / 'reports/split_manifest.csv')
    old = original.iloc[split.loc[split.split == 'test', 'row_index']]
    grid = probe()
    pairs = pd.read_csv(ML / 'data/benchmarks/lfw_face_match.csv')
    hybrid = pd.DataFrame([[score, 1, 1, *QUALITY[1]] for score in pairs.faceMatchScore], columns=FEATURES)
    report = {'model_version': MODEL_VERSION, 'baseline_version': manifest['version'],
              'class_order': CLASSES, 'seeds': SEEDS, 'quality_profiles': QUALITY,
              'candidate_sha256': hashlib.sha256((out / MODEL).read_bytes()).hexdigest()}
    for name, predict in [('baseline', baseline), ('candidate', lambda f: candidate_predict(f, out, tmp))]:
        result = {}
        for population, data in [('original', old), ('revised', fresh)]:
            p = predict(data)
            result[population] = matrix(data.target.to_numpy(), p)
            strong = (data.liveness_score >= .90) & (data.ocr_confidence_score >= .90)
            result[population]['strong_evidence'] = by_band(data.loc[strong], p[strong])
        result['perfect_evidence'] = by_band(grid, predict(grid))
        # New profiles and fractional scores were excluded from candidate selection.
        unseen = pd.DataFrame([[face, 1, 1, *q] for q in [[50, 135, 36], [120, 170, 50], [170, 155, 65]]
                               for face in np.arange(0.5, 100, 1)], columns=FEATURES)
        result['new_profiles'] = by_band(unseen, predict(unseen))
        conflicts = fresh[(fresh.face_match_score > 50) &
                          ((fresh.liveness_score < .25) | (fresh.ocr_confidence_score < .25))]
        conflict_pred = predict(conflicts)
        result['strong_face_weak_liveness_or_text'] = {
            label: int(sum(conflict_pred == label)) for label in CLASSES}
        p = predict(hybrid)
        result['benchmark_face_with_simulated_other_inputs'] = {
            kind: {label: int(sum(p[pairs.pair_type == kind] == label)) for label in CLASSES}
            for kind in ['genuine', 'impostor']}
        report[name] = result
    archived = json.loads((ML / 'reports/evaluation_report.json').read_text())
    assert archived['confusion_matrix_labels'] == CLASSES
    assert report['baseline']['original']['matrix'] == archived['confusion_matrix']
    (out / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('step', choices=['train', 'development', 'evaluate'])
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as directory:
        tmp = Path(directory)
        if args.step == 'train':
            train(args.out, tmp)
        elif args.step == 'development':
            cases = draw('development', [900, 300, 300])
            print(matrix(cases.target.to_numpy(), candidate_predict(cases, args.out, tmp)))
            grid = probe()
            print(by_band(grid, candidate_predict(grid, args.out, tmp)))
        else:
            evaluate(args.out, tmp)


if __name__ == '__main__':
    main()
