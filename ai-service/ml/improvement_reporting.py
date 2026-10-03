"""Render the frozen v3 comparison without recomputing or selecting on test."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'experiments/v3'


def publish():
    r=json.loads((OUT/'improvement_report.json').read_text())
    c=r['selected_validation']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig, axes=plt.subplots(1,2,figsize=(10,4))
    names=['Accuracy','Macro F1','Review recall']
    for offset,key,label in [(-.18,'incumbent','Saved v2'),(.18,'candidate','Selected v3')]:
        m=r[key]
        values=[m['accuracy'],m['macro_f1'],m['per_class']['review']['recall']]
        bars=axes[0].bar(np.arange(3)+offset,values,width=.36,label=label)
        axes[0].bar_label(bars,fmt='%.3f',fontsize=8,padding=3)
        counts=[m['errors']['Rejected -> Verified'],m['errors']['Manual Review -> Verified']]
        bars=axes[1].bar(np.arange(2)+offset,counts,width=.36,label=label)
        axes[1].bar_label(bars,fontsize=8,padding=3)
    axes[0].set_xticks(range(3),names);axes[0].set_ylim(0,1);axes[0].set_title('Higher is better')
    axes[1].set_xticks(range(2),['Rejected to Verified','Review to Verified']);axes[1].set_title('False approvals: lower is better')
    axes[0].legend();fig.suptitle('Same fresh 1,500 synthetic cases')
    fig.tight_layout();fig.savefig(OUT/'comparison.png',dpi=160);plt.close(fig)
    lines=['# KYC v3 improvement experiment','',
           f"Production promotion: **{r['promotion']['promoted']}**. {r['promotion']['reason']}",'',
           'Both rows below were evaluated on the SAME fresh 1,500 synthetic cases. The original v2 74.33% result used a different test set and must not be used as the before value here.','',
           '| Model | Accuracy | Macro F1 | Weighted F1 | Rejected → Verified | Manual Review → Verified |',
           '|---|---:|---:|---:|---:|---:|']
    for name,m in [('Saved v2 incumbent',r['incumbent']),('Selected v3 candidate',r['candidate'])]:
        lines.append(f"| {name} | {100*m['accuracy']:.3f}% | {m['macro_f1']:.6f} | {m['weighted_f1']:.6f} | {m['errors']['Rejected -> Verified']} | {m['errors']['Manual Review -> Verified']} |")
    lines+=['',f"Accuracy difference: **{100*r['accuracy_difference']:.3f} percentage points**.",
            f"Paired bootstrap 95% interval: {r['paired_uncertainty']['accuracy_difference_95_percent_interval']} (accuracy fraction).",
            f"Macro F1 difference: {r['macro_f1_difference']:.6f}; paired interval: {r['paired_uncertainty']['paired_bootstrap_macro_f1_difference_95_percent_interval']}.",'',
            '## Selected model and policy','',f"Candidate: **{c['candidate']}**.",
            f"Training-only hyperparameters: `{r['selected_training']['best_params']}`; CV macro F1: {r['selected_training']['cv_macro_f1']:.6f}.",
            f"Policy: {c['policy']}; review multiplier {c['review_multiplier']}; verification threshold {c['verified_threshold']}; verification margin {c['verified_margin']}.",
            'All six input features and the generator assumptions were retained. Quality transforms, where selected, are learned inside training folds. Probabilities are unchanged by the decision policy.','',
            '| Selection metrics | Accuracy | Macro F1 | Review recall | Rejected → Verified | Review → Verified |',
            '|---|---:|---:|---:|---:|---:|']
    for name,m in [('Comparable baseline',r['baseline_validation']),('Selected candidate',c)]:
        lines.append(f"| {name} | {m['accuracy']:.6f} | {m['macro_f1']:.6f} | {m['review_recall']:.6f} | {m['rejected_to_verified']} | {m['review_to_verified']} |")
    lines+=['','## Fresh per-class results','','| Model | Class | Precision | Recall | F1 |','|---|---|---:|---:|---:|']
    for name,m in [('v2',r['incumbent']),('v3',r['candidate'])]:
        for row in m['per_class'].values():
            lines.append(f"| {name} | {row['label']} | {row['precision']:.6f} | {row['recall']:.6f} | {row['f1']:.6f} |")
    for name in ['incumbent','candidate']:
        lines+=['',f'## {name} confusion matrix','',
                'Actual rows / predicted columns; order Verified, Manual Review, Rejected.','','```text',
                *[str(row) for row in r[name]['confusion_matrix']],'```']
    lines+=['','## Probability quality','','| Model | Log loss | Multiclass Brier |','|---|---:|---:|']
    for name in ['incumbent','candidate']:
        p=r[name]['probability_calibration']
        lines.append(f"| {name} | {p['log_loss']:.6f} | {p['multiclass_brier_sum']:.6f} |")
    lines+=['','## What was compared','','Four SVM variants (raw/power quality × native/explicit one-vs-rest), three calibration methods (sigmoid/isotonic/temperature), and native versus validation-selected review policies. Three new 24-point five-fold searches were run; the prior raw-native CV winner was reused with provenance. All policy/calibration variants are in `validation_candidates.csv`.','',
            '## Isolation and autonomy','','Original train=7,000; calibration=750; selection=750. Original test=1,500 retired. Fresh evaluation=1,500, generated only after selection freeze. Exact and near-duplicate checks cover all 11,500 rows. The test is used once for reported evaluation and a predeclared release acceptance check, not candidate tuning. Training checkpoints allow recovery from implementation errors; completed experiments are not silently rerun. No online learning exists.','',
            '## Permutation importance','','| Feature | Macro F1 decrease | Repeat SD |','|---|---:|---:|']
    for row in sorted(r['permutation_importance'],key=lambda row:row['importance'],reverse=True):
        lines.append(f"| {row['feature']} | {row['importance']:.6f} | {row['std']:.6f} |")
    lines+=['','## Limitations','',*[f'- {line}' for line in r['limitations']],
            '- The original data contains observationally identical components with different assumed adjudication outcomes. Their minimum population error contribution is 8%; other overlap can add more.',
            '- Accuracy improvements do not by themselves establish acceptable false-approval rates. Examine the exact counts above.',
            '- Local integration and API checks do not constitute remote Hugging Face deployment or live database validation.','',
            '## Files','']
    for p in sorted(OUT.iterdir()):
        if p.is_file(): lines.append(f'- [{p.name}](<{p.as_posix()}>)')
    lines+=['',f"- [Runner](<{(ROOT/'improve_model.py').as_posix()}>)",f"- [Saved-policy implementation](<{(ROOT/'decision_model.py').as_posix()}>)"]
    summary='\n'.join(lines)+'\n'
    (OUT/'SUMMARY.md').write_text(summary,encoding='utf-8')
    if r['promotion']['promoted']:
        (ROOT/'reports/TECHNICAL_SUMMARY.md').write_text(summary,encoding='utf-8')


if __name__=='__main__': publish()
