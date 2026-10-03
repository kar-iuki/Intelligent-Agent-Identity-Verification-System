"""Metrics and plots; executed after model/calibrator choices are frozen."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, log_loss, ConfusionMatrixDisplay)
try:
    from .schema import CLASSES, FEATURES, CLASS_KEYS, SEED
except ImportError:
    from schema import CLASSES, FEATURES, CLASS_KEYS, SEED


def evaluate(model, x, y):
    pred = model.predict(x)
    prob = model.predict_proba(x)
    prob = prob[:, [list(model.classes_).index(c) for c in CLASSES]]
    assert np.isfinite(prob).all() and np.allclose(prob.sum(axis=1), 1)
    onehot = np.column_stack([np.asarray(y) == c for c in CLASSES])
    cm = confusion_matrix(y, pred, labels=CLASSES)
    report = classification_report(y, pred, labels=CLASSES, output_dict=True, zero_division=0)
    bins = {}
    for j, name in enumerate(CLASSES):
        rows = []
        edges = np.linspace(0, 1, 11)
        for b, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
            mask = (prob[:, j] >= lo) & (prob[:, j] < hi if b < 9 else prob[:, j] <= hi)
            if mask.any():
                rows.append({'lower': float(lo), 'n': int(mask.sum()),
                             'mean_probability': float(prob[mask, j].mean()),
                             'observed_fraction': float(onehot[mask, j].mean())})
        bins[name] = rows
    errors = {f'{actual} -> {predicted}': int(cm[i, j]) for i, actual in enumerate(CLASSES)
              for j, predicted in enumerate(CLASSES) if i != j}
    # log_loss expects columns in lexicographic label order.
    order = np.argsort(CLASSES)
    result = {'accuracy': accuracy_score(y, pred), 'macro_f1': f1_score(y, pred, average='macro'),
              'weighted_f1': f1_score(y, pred, average='weighted'),
              'per_class': {k: {'label': name, **report[name], 'f1': report[name]['f1-score']} for k, name in zip(CLASS_KEYS, CLASSES)},
              'classification_report': report, 'confusion_matrix': cm.tolist(),
              'confusion_matrix_labels': CLASSES, 'errors': errors,
              'probability_calibration': {'log_loss': log_loss(y, prob[:, order], labels=sorted(CLASSES)),
                  'multiclass_brier_sum': float(np.mean(np.sum((prob-onehot)**2, axis=1))),
                  'brier_definition': 'Mean sum of squared errors over 3 classes, range [0,2].',
                  'classwise_ece_10_bins': {name: sum(r['n']*abs(r['mean_probability']-r['observed_fraction']) for r in bins[name])/len(y) for name in CLASSES},
                  'reliability_bins': bins}}
    return result, pred, prob


def model_plots(result, name, out):
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(np.array(result['confusion_matrix']), display_labels=CLASSES).plot(ax=ax, colorbar=False)
    ax.set(xlabel='Predicted class', ylabel='Actual class', title=name.replace('_', ' '))
    fig.tight_layout(); fig.savefig(out/f'{name}_confusion_matrix.png', dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], '--', color='gray')
    for label, rows in result['probability_calibration']['reliability_bins'].items():
        ax.plot([r['mean_probability'] for r in rows], [r['observed_fraction'] for r in rows], 'o-', label=label)
    ax.set(xlabel='Mean predicted probability', ylabel='Observed class fraction', title=f'{name}: reliability (10 bins)', xlim=(0, 1), ylim=(0, 1))
    ax.legend(); fig.tight_layout(); fig.savefig(out/f'{name}_calibration.png', dpi=150); plt.close(fig)


def distribution_plots(df, out):
    df.groupby('target')[FEATURES].describe(percentiles=[.05, .25, .5, .75, .95]).to_csv(out/'descriptive_statistics_by_class.csv')
    overlaps = {}
    for feature in FEATURES:
        stats = {label: {'mean': float(g[feature].mean()), 'std': float(g[feature].std()),
                        'min': float(g[feature].min()), 'max': float(g[feature].max()),
                        'p05': float(g[feature].quantile(.05)), 'p95': float(g[feature].quantile(.95))}
                 for label, g in df.groupby('target')}
        pairs = {}
        for i, a in enumerate(CLASSES):
            for b in CLASSES[i+1:]:
                lo, hi = max(stats[a]['p05'], stats[b]['p05']), min(stats[a]['p95'], stats[b]['p95'])
                pairs[a+' / '+b] = {'central_90_percent_intersection': [lo, hi] if hi >= lo else None}
        overlaps[feature] = {'class_statistics': stats, 'pairwise_overlap': pairs}
    (out/'distribution_overlap_diagnostics.json').write_text(json.dumps(overlaps, indent=2))
    for name in FEATURES:
        fig, ax = plt.subplots(figsize=(7, 4))
        bins = np.linspace(df[name].min(), df[name].max(), 45)
        for label in CLASSES:
            ax.hist(df.loc[df.target == label, name], bins=bins, density=True, histtype='step', linewidth=1.8, label=label)
        ax.set(xlabel=name, ylabel='Density', title=f'{name}: class overlap')
        ax.legend(); fig.tight_layout(); fig.savefig(out/f'distribution_{name}.png', dpi=150); plt.close(fig)
    corr = df[FEATURES].corr()
    corr.to_csv(out/'feature_correlations.csv')
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap='coolwarm')
    ax.set_xticks(range(6), FEATURES, rotation=50, ha='right'); ax.set_yticks(range(6), FEATURES)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center')
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(out/'correlation_matrix.png', dpi=150); plt.close(fig)


def importance_plot(table, name, out, error=None):
    frame = pd.DataFrame(table).sort_values('importance', ascending=True)
    frame.to_csv(out/f'{name}.csv', index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(frame.feature, frame.importance, xerr=frame[error] if error else None)
    ax.set(xlabel='Drop in test macro F1' if error else 'Mean decrease in impurity', title=name.replace('_', ' '))
    fig.tight_layout(); fig.savefig(out/f'{name}.png', dpi=150); plt.close(fig)


def paired_ablation(y, full_pred, identity_pred, repeats=1000):
    rng = np.random.default_rng(SEED)
    y = np.asarray(y)
    differences = []
    for _ in range(repeats):
        idx = rng.integers(0, len(y), len(y))
        differences.append(f1_score(y[idx], full_pred[idx], average='macro')-
                           f1_score(y[idx], identity_pred[idx], average='macro'))
    return {'paired_bootstrap_macro_f1_difference_95_percent_interval': np.quantile(differences, [.025, .975]).tolist(),
            'bootstrap_repeats': repeats, 'caveat': 'Conditional on this fitted pair and synthetic population; not real-world or training-seed uncertainty.'}
