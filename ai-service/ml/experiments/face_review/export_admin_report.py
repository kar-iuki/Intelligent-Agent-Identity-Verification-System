"""Export the saved comparison into the report shipped with the standalone Node backend."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def summarize(model, cases):
    matrix = model[cases]['matrix']
    return {
        'cases': sum(map(sum, matrix)),
        'accuracy': model[cases]['accuracy'],
        'macro_f1': model[cases]['macro_f1'],
    }


def build_report(comparison, scaler, scenarios):
    current, baseline = comparison['candidate'], comparison['baseline']
    metrics = current['revised']
    matrix = metrics['matrix']
    labels = comparison['class_order']
    keys = {'Verified': 'verified', 'Manual Review': 'review', 'Rejected': 'rejected'}
    per_class = {}
    for i, label in enumerate(labels):
        correct = matrix[i][i]
        actual = sum(matrix[i])
        predicted = sum(row[i] for row in matrix)
        per_class[keys[label]] = {
            'precision': correct / predicted if predicted else 0,
            'recall': correct / actual if actual else 0,
            'f1': 2 * correct / (actual + predicted) if actual + predicted else 0,
            'support': actual,
        }
    train = sum(scenarios['class_counts'].values())
    test = sum(map(sum, matrix))
    splits = {'train': train, 'validation': 1500, 'test': test}
    return {
        'model_version': comparison['model_version'],
        'baseline_version': comparison['baseline_version'],
        'accuracy': metrics['accuracy'],
        'macro_f1': metrics['macro_f1'],
        'weighted_f1': sum(row['f1'] * row['support'] for row in per_class.values()) / test,
        'per_class': per_class,
        'confusion_matrix': matrix,
        'confusion_matrix_labels': [keys[label] for label in labels],
        'correct_predictions': sum(matrix[i][i] for i in range(len(matrix))),
        'dataset_size': sum(splits.values()),
        'split_sizes': splits,
        'kernel': 'RBF', 'best_params': {'C': 10, 'gamma': 1},
        'features': scaler['features'],
        'comparisons': [
            {'sample': name, 'baseline': summarize(baseline, key), 'current': summarize(current, key)}
            for key, name in [('revised', 'Revised scenarios'), ('original', 'Original scenarios')]
        ],
        'face_review_probes': current['new_profiles']['25_through_50'],
        'baseline_face_review_probes': baseline['new_profiles']['25_through_50'],
    }


if __name__ == '__main__':
    inputs = [json.loads((HERE / name).read_text()) for name in ('comparison.json', 'scaler.json', 'scenarios.json')]
    report = build_report(*inputs)
    output = HERE.parents[3] / 'backend/src/data' / f"model-evaluation-{report['model_version']}.json"
    output.write_text(json.dumps(report, indent=2) + '\n')
