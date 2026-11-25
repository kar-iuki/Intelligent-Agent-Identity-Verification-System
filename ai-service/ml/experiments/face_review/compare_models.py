"""Compare v3.1.1 with retrained alternatives. Requires scikit-learn and libsvm-official."""
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd
from libsvm.svmutil import svm_load_model, svm_predict, svm_train
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import log_loss
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier

from run import CLASSES, FEATURES, HERE, MODEL, SEEDS, by_band, draw, matrix


def targets(frame):
    return np.asarray([CLASSES.index(label) for label in frame.target])


def scaled(frame, limits, n):
    values = frame[FEATURES[:n]].to_numpy()
    lo, hi = np.asarray(limits['min'])[:n], np.asarray(limits['max'])[:n]
    return np.clip((values - lo) / (hi - lo), 0, 1)


def svm_probabilities(model, x):
    _, _, probabilities = svm_predict([], x, model, '-b 1 -q')
    return np.asarray(probabilities)[:, np.argsort(model.get_labels())]


def evaluate(frame, probabilities):
    actual = targets(frame)
    predicted = probabilities.argmax(axis=1)
    labels = np.asarray(CLASSES)[predicted]
    result = matrix(frame.target.to_numpy(), labels)
    cm = np.asarray(result['matrix'])
    f1 = 2 * cm.diagonal() / (cm.sum(axis=0) + cm.sum(axis=1))
    strong = (frame.liveness_score >= .90) & (frame.ocr_confidence_score >= .90)
    result.update(
        weighted_f1=float(np.average(f1, weights=cm.sum(axis=1))),
        log_loss=float(log_loss(actual, probabilities, labels=range(3))),
        incorrect_verifications=int(cm[1:, 0].sum()),
        predicted_review=int(cm[:, 1].sum()),
        strong_evidence=by_band(frame.loc[strong], labels[strong]),
    )
    return result


def paired_accuracy_interval(actual, reference, other):
    # Resample matched predictions within each true class to keep the test mixture fixed.
    difference = (other.argmax(axis=1) == actual).astype(int) - (reference.argmax(axis=1) == actual)
    rng = np.random.default_rng(42)
    totals = np.zeros(5000)
    for label in range(3):
        subset = difference[actual == label]
        frequencies = np.bincount(subset + 1, minlength=3) / len(subset)
        counts = rng.multinomial(len(subset), frequencies, size=len(totals))
        totals += counts[:, 2] - counts[:, 0]
    return np.quantile(totals / len(actual), [.025, .975]).tolist()


def compare():
    train = draw('train', [3000, 2400, 1600])
    dev = draw('development', [900, 300, 300])
    y = targets(train)
    limits = json.loads((HERE / 'scaler.json').read_text())
    archive = json.loads((HERE / 'comparison.json').read_text())
    digest = hashlib.sha256((HERE / MODEL).read_bytes()).hexdigest()
    assert digest == archive['candidate_sha256']
    assert limits['classes'] == CLASSES and limits['features'] == FEATURES
    np.testing.assert_allclose(train[FEATURES].min(), limits['min'])
    np.testing.assert_allclose(train[FEATURES].max(), limits['max'])

    full = svm_load_model(str(HERE / MODEL))
    weights = len(y) / (len(CLASSES) * np.bincount(y))
    weight_options = ' '.join(f'-w{i} {w:.17g}' for i, w in enumerate(weights))
    identity = svm_train(y, scaled(train, limits, 3), f'-q -s 0 -t 2 -c 10 -g 1 -b 1 {weight_options}')

    grid = GridSearchCV(
        DecisionTreeClassifier(class_weight='balanced', random_state=42),
        {'max_depth': [3, 5, 8, None], 'min_samples_leaf': [5, 20, 50]},
        cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring='f1_macro',
        error_score='raise',
    ).fit(train[FEATURES], y)
    tree = grid.best_estimator_
    calibrated = CalibratedClassifierCV(FrozenEstimator(tree), method='sigmoid').fit(dev[FEATURES], targets(dev))

    test = draw('evaluation', [1800, 600, 600])
    probes = pd.DataFrame([[f, 1, 1, *quality] for quality in ([50, 135, 36], [120, 170, 50], [170, 155, 65])
                           for f in np.arange(.5, 100, 1)], columns=FEATURES)
    predictions = {
        'full_svm': lambda f: svm_probabilities(full, scaled(f, limits, 6)),
        'identity_only_svm': lambda f: svm_probabilities(identity, scaled(f, limits, 3)),
        'decision_tree': lambda f: tree.predict_proba(f[FEATURES]),
        'calibrated_decision_tree': lambda f: calibrated.predict_proba(f[FEATURES]),
    }
    report = {
        'svm_version': '3.1.1', 'saved_model_sha256': digest, 'classes': CLASSES, 'seeds': SEEDS,
        'library_versions': {name: version(name) for name in ['libsvm-official', 'scikit-learn', 'pandas', 'numpy']},
        'split_counts_in_class_order': {k: np.bincount(targets(v)).tolist() for k,v in
                                       [('train', train), ('development', dev), ('test', test)]},
        'tree_selection': {'best_parameters': grid.best_params_, 'mean_cv_macro_f1': grid.best_score_},
        'identity_svm': {'features': FEATURES[:3], 'C': 10, 'gamma': 1, 'class_weights': weights.tolist()},
        'models': {},
    }
    full_test = predictions['full_svm'](test)
    for name, predict in predictions.items():
        probabilities = full_test if name == 'full_svm' else predict(test)
        result = evaluate(test, probabilities)
        result['perfect_evidence_probes'] = by_band(probes, np.asarray(CLASSES)[predict(probes).argmax(axis=1)])
        if name == 'full_svm':
            assert result['matrix'] == archive['candidate']['revised']['matrix']
            assert result['perfect_evidence_probes'] == archive['candidate']['new_profiles']
        else:
            result['paired_accuracy_difference_vs_full_95pct'] = paired_accuracy_interval(targets(test), full_test, probabilities)
        report['models'][name] = result
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'comparison_models.json')
    args = parser.parse_args()
    args.output.write_text(json.dumps(compare(), indent=2, allow_nan=False) + '\n')
