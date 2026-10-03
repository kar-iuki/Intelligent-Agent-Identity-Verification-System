"""Readable measured results and complete file index, without recomputing metrics."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent


def publish_summary():
    r = json.loads((ROOT/'reports/evaluation_report.json').read_text())
    a = r['ablation_comparison']
    models = [('Full SVM', r), ('Identity-only SVM', r['identity_only_model']), ('Decision Tree', r['decision_tree'])]
    lines = ['# Recorded KYC experiment results', '',
             f"Model **{r['model_version']}**, trained {r['training_timestamp']}; seed {r['random_seed']}.",
             'All results below are from synthetic held-out data. No requested target accuracy was used.', '',
             '## Dataset and split', '', '| Partition | Verified | Manual Review | Rejected | Total |',
             '|---|---:|---:|---:|---:|']
    for name, counts in [('All', r['class_distribution']), *r['per_split_class_distributions'].items()]:
        lines.append(f"| {name} | {counts['Verified']} | {counts['Manual Review']} | {counts['Rejected']} | {sum(counts.values())} |")
    lines += ['', '## Model comparison', '', '| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Review → Verified |', '|---|---:|---:|---:|---:|---:|']
    for name, result in models:
        lines.append(f"| {name} | {result['accuracy']:.6f} | {result['macro_f1']:.6f} | {result['weighted_f1']:.6f} | {result['errors']['Rejected -> Verified']} | {result['errors']['Manual Review -> Verified']} |")
    for name, result in models:
        lines += ['', f'### {name}', '', f"Selected parameters: `{result['best_params']}`. Training CV macro F1: **{result['cv_macro_f1']:.6f}**.", '',
                  '| Class | Precision | Recall | F1 | Support |', '|---|---:|---:|---:|---:|']
        for name2, row in result['per_class'].items():
            lines.append(f"| {row['label']} | {row['precision']:.6f} | {row['recall']:.6f} | {row['f1-score']:.6f} | {int(row['support'])} |")
        lines += ['', 'Confusion matrix: actual rows / predicted columns; order Verified, Manual Review, Rejected.', '', '```text']
        lines += [str(row) for row in result['confusion_matrix']]
        lines += ['```', '', 'All off-diagonal errors:']
        lines += [f"- {key}: {value}" for key,value in result['errors'].items()]
    lines += ['', '## Probability quality', '', '| Model | Log loss | Multiclass Brier (sum) |', '|---|---:|---:|']
    for name, result in [*models, ('Decision Tree, sigmoid', r['decision_tree']['calibrated_comparison'])]:
        p = result['probability_calibration']
        lines.append(f"| {name} | {p['log_loss']:.6f} | {p['multiclass_brier_sum']:.6f} |")
    lines += ['', 'Lower is better. Brier is mean sum of three squared probability errors, range 0–2. SVM calibration uses validation only. Reliability diagrams and per-class ten-bin ECE are saved; synthetic calibration does not imply real certainty.', '',
              '## Importance', '', '| SVM feature | Mean macro F1 drop | Repeat SD |', '|---|---:|---:|']
    for row in sorted(r['svm_permutation_importance'], key=lambda x:x['importance'], reverse=True):
        lines.append(f"| {row['feature']} | {row['importance']:.6f} | {row['std']:.6f} |")
    lines += ['', '20 permutations; seed 42. SD is across repeats, not a population confidence interval.', '', '| Decision Tree feature | Impurity importance |', '|---|---:|']
    for row in sorted(r['decision_tree_feature_importance'], key=lambda x:x['importance'], reverse=True):
        lines.append(f"| {row['feature']} | {row['importance']:.6f} |")
    lines += ['', 'Tree impurity importance and SVM permutation drops are different quantities; correlated predictors can change both rankings.', '',
              '## Ablation', '', f"Full-minus-identity macro F1: **{a['macro_f1_difference_full_minus_identity']:.6f}**.",
              f"Paired bootstrap 95% interval: {a['paired_bootstrap_macro_f1_difference_95_percent_interval']} (1,000 replicates).",
              'Interpret this as evidence conditional on the simulator and these fitted models. It is not proof of production benefit. Both models were tuned independently using comparable training CV; six production features remain.', '',
              '## Duplicate and leakage diagnostics', '', '```json', json.dumps(r['duplicate_diagnostics'],indent=2), '```', '', '```json', json.dumps(r['leakage_diagnostics'],indent=2), '```', '',
              'Historical findings: see `legacy_methodology_audit.json`. Original data, scripts and model files are retained. Full methodology, API units, calibration policy and limitations are in `../README.md`.', '',
              '## Defence explanation', '',
              'The RBF SVM combines six upstream numerical verification signals. It does not process images. Face, liveness and OCR provide identity evidence; raw image-quality metrics provide context for unreliable captures. A training-only MinMaxScaler normalizes the scores, an RBF SVM learns nonlinear boundaries, and validation-only sigmoid calibration produces probabilities for Verified, Manual Review and Rejected. Results quantify performance under documented synthetic assumptions; independent real KYC evaluation is still required.', '',
              '## Limitations', '']
    lines += [f'- {s}' for s in r['limitations']]
    lines += ['', '## Interpretation of this run', '',
              ('Quality features did not improve macro F1 in this run.' if a['macro_f1_difference_full_minus_identity'] <= 0 else 'Quality features improved observed macro F1 in this run.'),
              'Classification metrics, security errors and probability quality must be considered separately.',
              f"The full model incorrectly verified {r['errors']['Rejected -> Verified']} of 300 Rejected cases and {r['errors']['Manual Review -> Verified']} of 300 Manual Review cases. These errors do not justify automatic operational approval. No test-guided retuning was performed.", '']
    (ROOT/'reports/TECHNICAL_SUMMARY.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    paths = [p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    repo = ROOT.parents[1]
    paths += [repo/p for p in ['ai-service/services/svmService.py', 'ai-service/routes/svmRoutes.py',
              'ai-service/tests/test_svm.py', 'ai-service/tests/test_kyc_experiment.py',
              'backend/src/services/accessControlService.js', 'backend/src/services/verificationService.js',
              'backend/tests/kycDecision.test.js', 'frontend/src/views/AdminModelEvaluation.vue',
              'ai-service/notebooks/01_distribution_analysis.ipynb', 'ai-service/notebooks/02_model_training.ipynb',
              'ai-service/notebooks/03_kyc_experiment_results.ipynb']]
    paths = sorted(set(paths))
    text = '# Experiment file index\n\nIncludes generated outputs, source files, benchmark inputs and preserved historical artifacts.\n\n'
    for p in paths:
        text += f'- [{p.relative_to(repo).as_posix()}](<{p.as_posix()}>)\n'
    (ROOT/'reports/FILE_INDEX.md').write_text(text, encoding='utf-8')


if __name__ == '__main__':
    publish_summary()
