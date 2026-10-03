"""Offline, reproducible KYC experiment. Test is accessed only after all fits.

Run from ai-service: python ml/train_model.py --version 2.0.0 --jobs 2
The validation partition calibrates frozen training-only classifiers. It is
not subsequently merged into training. CV owns a fresh scaler in each fold.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.inspection import permutation_importance
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from generate_dataset import generate_dataset
from schema import FEATURES, CLASSES, CLASS_KEYS, SEED, BOUNDS
from audit import audit_and_split, training_signal_audit
from evaluation import evaluate, model_plots, distribution_plots, importance_plot, paired_ablation

ROOT = Path(__file__).resolve().parent


def write_json(path, value):
    def convert(v):
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, np.generic): return v.item()
        raise TypeError(type(v).__name__)
    path.write_text(json.dumps(value, indent=2, default=convert, allow_nan=False), encoding='utf-8')


def tune_svm(x, y, jobs, out, name):
    estimator = Pipeline([('scaler', MinMaxScaler(clip=True)),
                          ('svm', SVC(kernel='rbf', class_weight='balanced', random_state=SEED))])
    grid = GridSearchCV(estimator, {'svm__C': [.1, 1, 10, 100],
                                  'svm__gamma': [.001, .01, .1, 1, 'scale', 'auto']},
                        cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                        scoring='f1_macro', n_jobs=jobs, error_score='raise', return_train_score=True)
    grid.fit(x, y)
    pd.DataFrame(grid.cv_results_).to_csv(out/f'{name}_grid_search.csv', index=False)
    print(f'{name}: {grid.best_params_}, CV macro F1={grid.best_score_:.6f}', flush=True)
    return grid.best_estimator_, {'best_params': {k.replace('svm__', ''): v for k, v in grid.best_params_.items()},
                                 'cv_macro_f1': grid.best_score_, 'cv_folds': 5,
                                 'cv_scoring': 'f1_macro', 'candidate_count': 24}


def calibrate(model, x_val, y_val):
    calibrated = CalibratedClassifierCV(FrozenEstimator(model), method='sigmoid')
    calibrated.fit(x_val, y_val)
    return calibrated


def legacy_audit():
    from sklearn.model_selection import train_test_split
    old = pd.read_csv(ROOT/'data'/'synthetic_verification_dataset.csv')
    cols = list(old.columns[:-1])
    train, hold = train_test_split(np.arange(len(old)), test_size=.3, stratify=old.label, random_state=SEED)
    val, test = train_test_split(hold, test_size=.5, stratify=old.label.iloc[hold], random_state=SEED)
    h = pd.util.hash_pandas_object(old[cols], index=False)
    z = old[cols].to_numpy()/np.array([100, 1, 1, 300, 255, 127.5])
    from scipy.spatial import cKDTree
    near = cKDTree(z).query_pairs(.005, p=np.inf)
    stumps = {c: float(GridSearchCV(DecisionTreeClassifier(random_state=SEED), {'max_depth': [2, 3]},
              scoring='f1_macro', cv=StratifiedKFold(5, shuffle=True, random_state=SEED)).fit(old.iloc[train][[c]], old.label.iloc[train]).best_score_) for c in cols}
    return {'records': len(old), 'counts': old.label.value_counts().to_dict(),
            'exact_duplicates': int(old.duplicated(cols).sum()),
            'conflicting_vectors': int((old.groupby(cols).label.nunique()>1).sum()),
            'train_test_duplicate_vectors': len(set(h.iloc[train])&set(h.iloc[test])),
            'near_duplicate_pairs_within_point005_fixed_range_each_feature': len(near),
            'single_feature_tree_training_cv_macro_f1': stumps,
            'findings': ['Labels assigned before independent class-specific clipped distributions.',
                         'All six feature ranges nearly isolate classes; quality is an artificial class proxy.',
                         'Small noise does not remove multivariate separation; old report accuracy=1.',
                         'Training script fits scaler on training only, but hard-codes notebook hyperparameters.',
                         'Notebook scales all training rows before GridSearchCV: CV-fold preprocessing leakage.',
                         'No evidence of direct target column or final test rows passed to model fit in inspected code.',
                         'No automatic duplicate or contamination checks; historical test reuse cannot be proven absent.',
                         'Benchmark score files exist but old generator does not derive its parameters from them.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='2.0.0')
    parser.add_argument('--config')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    out, models = ROOT/'reports', ROOT/'models'
    out.mkdir(exist_ok=True); models.mkdir(exist_ok=True)
    df, generation = generate_dataset(args.config)
    splits, duplicates = audit_and_split(df)
    dataset = ROOT/'data'/'kyc_synthetic_dataset_10000.csv'
    df.to_csv(dataset, index=False)
    write_json(dataset.with_suffix('.metadata.json'), generation)
    split_frame = pd.DataFrame({'row_index': np.arange(len(df)), 'split': ''})
    for name, idx in splits.items(): split_frame.loc[idx, 'split'] = name
    split_frame.to_csv(out/'split_manifest.csv', index=False)
    tr, va, te = [splits[k] for k in ['train', 'validation', 'test']]
    x, y = df[FEATURES].to_numpy(), df.target.to_numpy()
    print(f'Generated {len(df)} rows; train={len(tr)}, validation={len(va)}, test={len(te)}', flush=True)
    # Audit uses training CV only. No test-based generation/model changes.
    signal_audit = training_signal_audit(df, tr)
    write_json(out/'legacy_methodology_audit.json', legacy_audit())
    full_pipeline, full_selection = tune_svm(x[tr], y[tr], args.jobs, out, 'full_svm')
    identity_pipeline, identity_selection = tune_svm(x[tr, :3], y[tr], args.jobs, out, 'identity_svm')
    tree_grid = GridSearchCV(DecisionTreeClassifier(random_state=SEED, class_weight='balanced'),
                            {'max_depth': [3, 5, 8, None], 'min_samples_leaf': [5, 20, 50]},
                            scoring='f1_macro', cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                            n_jobs=args.jobs, error_score='raise')
    tree_grid.fit(x[tr], y[tr])
    pd.DataFrame(tree_grid.cv_results_).to_csv(out/'decision_tree_grid_search.csv', index=False)
    tree = tree_grid.best_estimator_
    scaler = full_pipeline.named_steps['scaler']
    identity_scaler = identity_pipeline.named_steps['scaler']
    assert scaler.n_samples_seen_ == len(tr)
    assert np.array_equal(scaler.data_min_, x[tr].min(axis=0))
    full = calibrate(full_pipeline.named_steps['svm'], scaler.transform(x[va]), y[va])
    identity = calibrate(identity_pipeline.named_steps['svm'], identity_scaler.transform(x[va, :3]), y[va])
    calibrated_tree = calibrate(tree, x[va], y[va])
    write_json(out/'frozen_experiment_protocol.json', {
        'version': args.version, 'seed': SEED, 'dataset_sha256': hashlib.sha256(dataset.read_bytes()).hexdigest(),
        'full_selection': full_selection, 'identity_selection': identity_selection,
        'tree_selection': tree_grid.best_params_, 'calibration': 'Sigmoid on validation only, frozen train-only estimators',
        'test_policy': 'All generation, hyperparameters, calibration and 6-feature deployment fixed before final test evaluation',
        'frozen_at': datetime.now(timezone.utc).isoformat()})
    print('All models and sigmoid calibrators frozen. Beginning final held-out evaluation.', flush=True)
    full_result, full_pred, full_prob = evaluate(full, scaler.transform(x[te]), y[te])
    identity_result, identity_pred, _ = evaluate(identity, identity_scaler.transform(x[te, :3]), y[te])
    tree_result, _, _ = evaluate(tree, x[te], y[te])
    tree_cal_result, _, _ = evaluate(calibrated_tree, x[te], y[te])
    full_result.update(full_selection); identity_result.update(identity_selection)
    tree_result.update(best_params=tree_grid.best_params_, cv_macro_f1=tree_grid.best_score_, calibrated_comparison=tree_cal_result)
    perm = permutation_importance(full, scaler.transform(x[te]), y[te], scoring='f1_macro',
                                  n_repeats=20, random_state=SEED, n_jobs=args.jobs)
    table = [{'feature': name, 'importance': float(mean), 'std': float(sd), 'repeats': vals.tolist()}
             for name, mean, sd, vals in zip(FEATURES, perm.importances_mean, perm.importances_std, perm.importances)]
    tree_table = [{'feature': name, 'importance': float(v)} for name, v in zip(FEATURES, tree.feature_importances_)]
    importance_plot([{k: v for k,v in row.items() if k != 'repeats'} for row in table], 'svm_permutation_importance', out, 'std')
    importance_plot(tree_table, 'decision_tree_feature_importance', out)
    for name, result in [('full_svm', full_result), ('identity_only_svm', identity_result), ('decision_tree', tree_result)]:
        model_plots(result, name, out)
    distribution_plots(df, out)
    ablation = {'full': full_result, 'identity_only': identity_result,
                'macro_f1_difference_full_minus_identity': full_result['macro_f1']-identity_result['macro_f1'],
                **paired_ablation(y[te], full_pred, identity_pred)}
    write_json(out/'ablation_comparison.json', ablation)
    libraries = {p: importlib.metadata.version(p) for p in ['scikit-learn', 'numpy', 'scipy', 'pandas', 'joblib', 'matplotlib', 'flask']}
    trained_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    report = {**full_result, 'model_version': args.version, 'training_timestamp': trained_at, 'training_date': trained_at,
              'random_seed': SEED, 'dataset_size': len(df), 'total_records': len(df),
              'split_sizes': {k: len(v) for k,v in splits.items()},
              'class_distribution': df.target.value_counts().to_dict(),
              'per_split_class_distributions': {k: df.iloc[v].target.value_counts().to_dict() for k,v in splits.items()},
              'features': FEATURES, 'feature_bounds': BOUNDS, 'kernel': 'rbf', 'feature_generation_parameters': generation,
              'library_versions': libraries, 'python_version': platform.python_version(),
              'svm_parameters': full_pipeline.named_steps['svm'].get_params(),
              'scaler_parameters': scaler.get_params(), 'scaler_training_min': scaler.data_min_.tolist(),
              'scaler_training_max': scaler.data_max_.tolist(), 'scaler_samples_seen': int(scaler.n_samples_seen_),
              'svm_permutation_importance': table, 'decision_tree_feature_importance': tree_table,
              'decision_tree': tree_result, 'identity_only_model': identity_result, 'ablation_comparison': ablation,
              'duplicate_diagnostics': duplicates,
              'leakage_diagnostics': {
                  'split_rows_disjoint': True, 'features_exclude_target_and_scenario_ids': True,
                  'scaler_fit': 'Each CV training fold; final scaler on 7000 training rows only.',
                  'tuning': '5-fold stratified training CV only, both SVMs and tree.',
                  'calibration': 'Frozen estimators fitted on train; sigmoid calibrators fitted on 1500 validation rows only.',
                  'test': '1500 rows used only for final metrics, diagnostic importance, plots and paired uncertainty, never selection.',
                  'synthetic_label_limitation': 'Outcomes assigned by assumed scenarios, not real adjudication. Some scenarios intentionally have identical observable distributions under different latent outcomes.',
                  'single_feature_training_cv_macro_f1': signal_audit,
                  'benchmark_limitations': 'Local measurement files reused as distribution evidence, not independent real-world validation. Raw benchmark images not rerun in this experiment.',
                  'near_perfect_trigger': full_result['accuracy'] >= .98,
                  'quality_dominates_permutation': max(table, key=lambda r: r['importance'])['feature'] in FEATURES[3:],
                  'test_experiments_run': 1},
              'limitations': ['Synthetic joint distributions and adjudication labels are assumptions.',
                             '60/20/20 is an experimental allocation, not prevalence.',
                             'MIDV score is text agreement, not proof of document authenticity.',
                             'LFW and NUAA are limited benchmarks; no demographic, modern attack or device shift validation.',
                             'Calibration is for this synthetic population, not real-world certainty.',
                             'Clipping outside training extrema may conceal production distribution shift.',
                             'No online learning; explicit offline retraining needs confirmed real labels.']}
    write_json(out/'evaluation_report.json', report)
    joblib.dump(full, models/'svm_kyc_model.pkl')
    joblib.dump(scaler, models/'scaler.pkl')
    joblib.dump(tree, models/'decision_tree_model.pkl')
    joblib.dump(calibrated_tree, models/'decision_tree_calibrated.pkl')
    joblib.dump(identity, models/'identity_only_svm.pkl')
    joblib.dump(identity_scaler, models/'identity_only_scaler.pkl')
    (models/'model_version.txt').write_text(f'{args.version}\ntrained_at={trained_at}\n', encoding='utf-8')
    # Validate the exact serialization path deployed by Flask.
    loaded = joblib.load(models/'svm_kyc_model.pkl')
    loaded_x = joblib.load(models/'scaler.pkl').transform(x[te])
    assert np.array_equal(loaded.predict(loaded_x), full_pred)
    assert np.allclose(loaded.predict_proba(loaded_x)[:, [list(loaded.classes_).index(c) for c in CLASSES]], full_prob)
    manifest = {'version': args.version, 'features': FEATURES, 'classes': list(full.classes_),
                'library_versions': libraries, 'dataset_sha256': hashlib.sha256(dataset.read_bytes()).hexdigest(),
                'artifacts': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in models.glob('*.pkl')}}
    write_json(models/'artifact_manifest.json', manifest)
    for name, result in [('Full SVM', full_result), ('Identity SVM', identity_result), ('Decision Tree', tree_result)]:
        print(name, json.dumps({k: result[k] for k in ['accuracy', 'macro_f1', 'confusion_matrix', 'errors']}), flush=True)
    print('Artifacts saved; reload parity verified.', flush=True)
    from reporting import publish_summary
    publish_summary()


if __name__ == '__main__':
    main()
