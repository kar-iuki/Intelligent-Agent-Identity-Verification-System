"""Automated offline improvement experiment. Never changes generator labels.

Train/CV: original 7000. Calibration: 750. Selection: disjoint 750.
Retired original test is not used. Fresh evaluation is drawn only after freeze.
Usage: python ml/improve_model.py --jobs 3 --promote
"""
import argparse
import hashlib
import itertools
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, log_loss
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.decision_model import DecisionPolicyClassifier, QualityShapeTransformer
from ml.generate_dataset import generate_dataset
from ml.schema import FEATURES, CLASSES, SEED
from ml.evaluation import evaluate, model_plots, importance_plot, paired_ablation

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'experiments'/'v3'


def write_json(path, value):
    def convert(v):
        if isinstance(v, np.ndarray): return v.tolist()
        if isinstance(v, np.generic): return v.item()
        raise TypeError(type(v).__name__)
    path.write_text(json.dumps(value, indent=2, default=convert, allow_nan=False), encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(y, pred):
    cm = confusion_matrix(y, pred, labels=CLASSES)
    return {'accuracy': float(accuracy_score(y, pred)), 'macro_f1': float(f1_score(y, pred, average='macro')),
            'rejected_to_verified': int(cm[2, 0]), 'review_to_verified': int(cm[1, 0]),
            'review_recall': float(cm[1, 1]/cm[1].sum())}


def fit_variant(name, x, y, jobs):
    checkpoint = OUT/f'{name}_training.pkl'
    if checkpoint.exists():
        print(f'Resuming frozen training checkpoint {name}', flush=True)
        scaler, native, info = joblib.load(checkpoint)
        native.steps = [(key, step) for key, step in native.steps if step != 'passthrough']
        return scaler, native, info
    ovr = name.endswith('ovr')
    svm = SVC(kernel='rbf', class_weight='balanced', random_state=SEED, cache_size=300)
    classifier = OneVsRestClassifier(svm, n_jobs=1) if ovr else svm
    pipe = Pipeline([('scaler', MinMaxScaler(clip=True)),
                     ('quality', QualityShapeTransformer() if name.startswith('power') else 'passthrough'),
                     ('classifier', classifier)])
    if name == 'raw_native':
        # These hyperparameters were selected by the prior train-only 24-point CV.
        prior = json.loads((ROOT/'legacy_v2/reports/frozen_experiment_protocol.json').read_text())
        assert prior['dataset_sha256'] == digest(ROOT/'data/kyc_synthetic_dataset_10000.csv')
        previous_selection = prior['full_selection']
        pipe.set_params(**{f'classifier__{k}':v for k,v in previous_selection['best_params'].items()}).fit(x, y)
        info = {'best_params': previous_selection['best_params'], 'cv_macro_f1':previous_selection['cv_macro_f1'],
                'cv_source':'legacy_v2/reports/full_svm_grid_search.csv (same training rows)'}
    else:
        prefix = 'classifier__estimator__' if ovr else 'classifier__'
        grid = GridSearchCV(pipe, {prefix+'C':[.1, 1, 10, 100],
                                  prefix+'gamma':[.001, .01, .1, 1, 'scale', 'auto']},
                            scoring={'macro_f1':'f1_macro', 'accuracy':'accuracy'}, refit='macro_f1',
                            cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                            n_jobs=jobs, pre_dispatch=jobs, error_score='raise')
        grid.fit(x, y)
        pd.DataFrame(grid.cv_results_).to_csv(OUT/f'{name}_grid.csv', index=False)
        pipe = grid.best_estimator_
        info = {'best_params':{k.replace(prefix,''):v for k,v in grid.best_params_.items()},
                'cv_macro_f1':float(grid.best_score_), 'cv_source':f'{name}_grid.csv'}
    # Only the raw MinMaxScaler is saved separately. The quality transform stays
    # inside the model; both transformations were fitted solely on training rows.
    scaler = pipe.named_steps['scaler']
    native = Pipeline([(key, step) for key, step in pipe.steps[1:] if step != 'passthrough'])
    result = (scaler, native, info)
    joblib.dump(result, checkpoint)
    print(f'{name}: {info}', flush=True)
    return result


def select_policy(candidates, x_cal, y_cal, x_select, y_select):
    records, fitted = [], {}
    for name, (scaler, native, info) in candidates.items():
        for method in ['sigmoid','isotonic','temperature']:
            calibrated = CalibratedClassifierCV(FrozenEstimator(native), method=method)
            calibrated.fit(scaler.transform(x_cal), y_cal)
            key = f'{name}_{method}'
            fitted[key] = (scaler, native, calibrated, info)
            prob = calibrated.predict_proba(scaler.transform(x_select))
            loss = float(log_loss(y_select, prob, labels=calibrated.classes_))
            # Native boundaries test the effect of calibration on decisions.
            native_pred = native.predict(scaler.transform(x_select))
            records.append({'candidate':key, 'policy':'native', 'review_multiplier':1.,
                            'verified_threshold':0., 'verified_margin':0.,
                            'log_loss':loss, **compact(y_select, native_pred)})
            for weight, threshold, margin in itertools.product([1.,1.25,1.5,2.], [0.,.5,.6,.7,.8], [0.,.1]):
                policy = DecisionPolicyClassifier(calibrated, native, review_multiplier=weight,
                                                  verified_threshold=threshold, verified_margin=margin)
                records.append({'candidate':key, 'policy':'probability', 'review_multiplier':weight,
                                'verified_threshold':threshold, 'verified_margin':margin,
                                'log_loss':loss, **compact(y_select, policy.decide(prob))})
    table = pd.DataFrame(records)
    baseline = table[(table.candidate=='raw_native_sigmoid') & (table.policy=='probability') &
                     (table.review_multiplier==1) & (table.verified_threshold==0) & (table.verified_margin==0)].iloc[0]
    # Guardrails are relative to an independently selected/calibrated incumbent,
    # not hand-chosen safety limits or test-derived thresholds.
    table['eligible'] = ((table.macro_f1 >= baseline.macro_f1-1e-12) &
                         (table.rejected_to_verified <= baseline.rejected_to_verified) &
                         (table.review_to_verified <= baseline.review_to_verified) &
                         (table.review_recall >= baseline.review_recall-1e-12))
    table = table.sort_values(['eligible','accuracy','macro_f1','log_loss','candidate'],
                              ascending=[False,False,False,True,True], kind='stable')
    table.to_csv(OUT/'validation_candidates.csv', index=False)
    chosen = table.iloc[0].to_dict()
    scaler, native, calibrated, info = fitted[chosen['candidate']]
    policy = DecisionPolicyClassifier(calibrated, native, chosen['policy'], chosen['review_multiplier'],
                                     chosen['verified_threshold'], chosen['verified_margin'])
    # Every architecture's unmodified probability-argmax validation metrics are
    # retained to explain calibration tradeoffs without selecting on fresh test.
    summaries = table[(table.policy=='probability') & (table.review_multiplier==1) &
                      (table.verified_threshold==0) & (table.verified_margin==0)].to_dict('records')
    return scaler, policy, info, chosen, baseline.to_dict(), summaries


def cross_dataset_audit(existing, fresh):
    from scipy.spatial import cKDTree
    combined = pd.concat([existing, fresh], ignore_index=True)
    x = combined[FEATURES].to_numpy()
    exact = int(combined.duplicated(FEATURES).sum())
    z = x.copy(); z[:,0] /= .1; z[:,1:3] /= .001
    z[:,3] = np.log1p(z[:,3])/.01; z[:,4:] /= .1
    pairs = cKDTree(z).query_pairs(1, p=np.inf, output_type='ndarray')
    assert exact==0 and len(pairs)==0, 'Fresh/old duplicates require investigation before evaluation'
    return {'combined_rows':len(combined), 'exact_duplicate_vectors':exact, 'near_duplicate_pairs':len(pairs),
            'definition':'All differences <= face .1, live .001, OCR .001, log1p(blur) .01, brightness .1, contrast .1'}


def comparison_intervals(y, new, old):
    result = paired_ablation(y, new, old)
    rng = np.random.default_rng(SEED)
    correct_difference = (new==y).astype(float)-(old==y).astype(float)
    values=[float(correct_difference[rng.integers(0,len(y),len(y))].mean()) for _ in range(1000)]
    result['accuracy_difference_95_percent_interval']=np.quantile(values,[.025,.975]).tolist()
    return result


def promotion(out_report, scaler, model):
    old = out_report['incumbent']; new = out_report['candidate']
    # One predeclared release acceptance check; failure retains v2 with no retry,
    # candidate switching, or further test-guided fitting.
    passed = (new['accuracy'] > old['accuracy'] and new['macro_f1'] >= old['macro_f1'] and
              new['errors']['Rejected -> Verified'] <= old['errors']['Rejected -> Verified'] and
              new['errors']['Manual Review -> Verified'] <= old['errors']['Manual Review -> Verified'])
    if not passed:
        return {'promoted':False, 'reason':'Fresh-test release gate did not pass; incumbent retained without test-guided retuning.'}
    models = ROOT/'models'
    joblib.dump(model, models/'svm_kyc_model.pkl')
    joblib.dump(scaler, models/'scaler.pkl')
    timestamp = out_report['training_timestamp']
    (models/'model_version.txt').write_text(f'3.0.0\ntrained_at={timestamp}\n')
    old_manifest=json.loads((ROOT/'legacy_v2/models/artifact_manifest.json').read_text())
    manifest={**old_manifest, 'version':'3.0.0', 'classes':list(model.classes_),
              'decision_policy':model.decision_policy,
              'artifacts':{p.name:digest(p) for p in models.glob('*.pkl')}}
    write_json(models/'artifact_manifest.json',manifest)
    previous_report=json.loads((ROOT/'legacy_v2/reports/evaluation_report.json').read_text())
    report={**previous_report,**new,'model_version':'3.0.0','training_date':timestamp, 'training_timestamp':timestamp,
            'random_seed':SEED,'dataset_size':10000,'total_records':10000,
            'split_sizes':{'train':7000,'validation':1500,'test':1500},
            'split_note':'Test metrics use a new independent 1500-row draw. Original 1500 test rows are retired, not training data.',
            'training_records':7000,'calibration_records':750,'selection_records':750,'fresh_test_records':1500,
            'features':FEATURES,'kernel':'rbf',**out_report['selected_training'],
            'decision_policy':model.decision_policy,'svm_permutation_importance':out_report['permutation_importance'],
            'svm_parameters':{'kernel':'rbf','class_weight':'balanced','random_state':SEED,
                              **out_report['selected_training']['best_params'],
                              'architecture':out_report['selected_validation']['candidate']},
            'decision_tree':out_report['reference_models']['decision_tree'],
            'identity_only_model':out_report['reference_models']['identity_only'],
            'ablation_comparison':{'status':'V3 comparison to saved v2 identity model is not a controlled feature ablation.',
                                  'prior_controlled_ablation':'legacy_v2/reports/ablation_comparison.json'},
            'experiment_report':'experiments/v3/improvement_report.json',
            'incumbent_fresh_comparison':old,'limitations':out_report['limitations'],
            'duplicate_diagnostics':out_report['duplicate_diagnostics'],
            'leakage_diagnostics':{'training_only_cv':True,'calibration_selection_disjoint':True,
                                   'retired_test_used':False,'fresh_test_after_selection_freeze':True,
                                   'test_used_for_release_gate_not_tuning':True},
            'protocol':out_report['protocol']}
    write_json(ROOT/'reports/evaluation_report.json',report)
    # Other v2 comparison plots stay archived; replace the production SVM plots.
    model_plots(new,'full_svm',ROOT/'reports')
    model_plots(out_report['reference_models']['decision_tree'],'decision_tree',ROOT/'reports')
    model_plots(out_report['reference_models']['identity_only'],'identity_only_svm',ROOT/'reports')
    importance_plot(out_report['permutation_importance'],'svm_permutation_importance',ROOT/'reports','std')
    write_json(ROOT/'reports/ablation_comparison.json',report['ablation_comparison'])
    return {'promoted':True,'reason':'Passed predeclared release gate: accuracy increased, macro F1 and both false-verification counts did not worsen.'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--jobs',type=int,default=3)
    parser.add_argument('--promote',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'improvement_report.json').exists():
        raise SystemExit('Completed experiment exists. Inspect it; do not repeatedly reuse this test draw.')
    dataset=ROOT/'data/kyc_synthetic_dataset_10000.csv'
    config=ROOT/'generation_config.json'
    df=pd.read_csv(dataset)
    manifest=pd.read_csv(ROOT/'legacy_v2/reports/split_manifest.csv')
    tr=manifest.loc[manifest.split=='train','row_index'].to_numpy()
    va=manifest.loc[manifest.split=='validation','row_index'].to_numpy()
    cal,sel=train_test_split(va,test_size=.5,stratify=df.target.iloc[va],random_state=SEED)
    assert not(set(tr)&set(cal) or set(tr)&set(sel) or set(cal)&set(sel))
    fresh_seed=int(np.random.SeedSequence(SEED).spawn(1)[0].generate_state(1)[0])
    protocol={'version':'3.0.0','seed':SEED,'fresh_test_seed':fresh_seed,
              'dataset_sha256':digest(dataset),'generator_config_sha256':digest(config),
              'generator_source_sha256':digest(ROOT/'generate_dataset.py'),
              'architectures':['raw_native','power_native','raw_ovr','power_ovr'],
              'grid_C':[.1,1,10,100],'grid_gamma':[.001,.01,.1,1,'scale','auto'],
              'calibrations':['sigmoid','isotonic','temperature'],
              'cv':'5-fold training-only macro F1; accuracy also recorded',
              'partitions':{'train':7000,'calibration':750,'selection':750,'retired_test':1500,'new_test':1500},
              'selection':'Maximum selection accuracy with macro F1, Manual Review recall and both false-verification counts no worse than raw-native-sigmoid baseline; tie macro F1 then log loss.',
              'release_gate':'Strictly higher fresh accuracy, macro F1 not lower, neither false-verification count higher than saved v2 on same fresh rows. Failure retains v2; no retries.',
              'no_online_learning':True,'label_generator_changed':False,
              'fresh_test_generated_after_freeze':True}
    protocol_path=OUT/'protocol.json'
    if protocol_path.exists():
        assert json.loads(protocol_path.read_text())==protocol,'Checkpoint protocol mismatch'
    write_json(protocol_path,protocol)
    pd.DataFrame([{'row_index':int(i),'split':name} for name,ids in [('train',tr),('calibration',cal),('selection',sel)] for i in ids]).to_csv(OUT/'development_split_manifest.csv',index=False)
    x=df[FEATURES].to_numpy();y=df.target.to_numpy()
    candidates={name:fit_variant(name,x[tr],y[tr],args.jobs) for name in protocol['architectures']}
    scaler,model,info,chosen,baseline,summaries=select_policy(candidates,x[cal],y[cal],x[sel],y[sel])
    print('VALIDATION WINNER',json.dumps(chosen),flush=True)
    print('VALIDATION BASELINE',json.dumps(baseline),flush=True)
    write_json(OUT/'selection_frozen.json',{'selected':chosen,'baseline':baseline,'training':info,
               'frozen_at':datetime.now(timezone.utc).isoformat()})
    joblib.dump(scaler,OUT/'candidate_scaler.pkl');joblib.dump(model,OUT/'candidate_model.pkl')
    # Only now create and inspect the fresh evaluation draw. No regeneration or
    # alternative seed selection based on scores is permitted.
    fresh,meta=generate_dataset(seed=fresh_seed,record_counts={'Verified':900,'Manual Review':300,'Rejected':300})
    fresh.to_csv(OUT/'fresh_evaluation_1500.csv',index=False)
    write_json(OUT/'fresh_evaluation_metadata.json',meta)
    duplicates=cross_dataset_audit(df,fresh)
    xt=fresh[FEATURES].to_numpy();yt=fresh.target.to_numpy()
    new,pred,_=evaluate(model,scaler.transform(xt),yt)
    old_model=joblib.load(ROOT/'legacy_v2/models/svm_kyc_model.pkl')
    old_scaler=joblib.load(ROOT/'legacy_v2/models/scaler.pkl')
    old,old_pred,_=evaluate(old_model,old_scaler.transform(xt),yt)
    permutation=permutation_importance(model,scaler.transform(xt),yt,scoring='f1_macro',n_repeats=20,random_state=SEED,n_jobs=args.jobs)
    importance=[{'feature':f,'importance':float(m),'std':float(s)} for f,m,s in zip(FEATURES,permutation.importances_mean,permutation.importances_std)]
    importance_plot(importance,'svm_permutation_importance',OUT,'std')
    model_plots(new,'candidate',OUT);model_plots(old,'incumbent',OUT)
    # Same fresh data also permit a descriptive reference to the saved tree and
    # identity-only models; these are never eligible for production selection.
    references={}
    for name,model_name,scaler_name in [('decision_tree','decision_tree_model.pkl',None),
                                       ('identity_only','identity_only_svm.pkl','identity_only_scaler.pkl')]:
        ref=joblib.load(ROOT/'legacy_v2/models'/model_name)
        xx=xt if scaler_name is None else joblib.load(ROOT/'legacy_v2/models'/scaler_name).transform(xt[:,:3])
        references[name]=evaluate(ref,xx,yt)[0]
    report={'training_timestamp':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'protocol':protocol,'selected_validation':chosen,'baseline_validation':baseline,
            'selected_training':info,'calibration_comparisons_on_selection':summaries,
            'candidate':new,'incumbent':old,'reference_models':references,
            'accuracy_difference':new['accuracy']-old['accuracy'],
            'macro_f1_difference':new['macro_f1']-old['macro_f1'],
            'paired_uncertainty':comparison_intervals(yt,pred,old_pred),
            'permutation_importance':importance,'duplicate_diagnostics':duplicates,
            'fresh_dataset_sha256':digest(OUT/'fresh_evaluation_1500.csv'),
            'limitations':['Fresh synthetic draw from the SAME assumptions; not independent real-world validation.',
                           'Previously observed v2 results motivated the hypotheses; original test was retired.',
                           'Calibration and selection are disjoint but small (750 each); searching policies can overfit selection.',
                           'Isotonic calibration may overfit small calibration samples; temperature can preserve poor decision rankings.',
                           'Latent review and genuine scenarios can share observed distributions; missing evidence remains irreducible.',
                           'Decision-policy preferences do not change calibrated probability values.',
                           'Quality transform and calibrators are static; no online learning.']}
    restored=joblib.load(OUT/'candidate_model.pkl')
    assert np.array_equal(restored.predict(scaler.transform(xt)),pred)
    report['promotion']=promotion(report,scaler,model) if args.promote else {'promoted':False,'reason':'Promotion not requested'}
    write_json(OUT/'improvement_report.json',report)
    from ml.improvement_reporting import publish
    publish()
    print('FINAL',json.dumps({k:report[k] for k in ['accuracy_difference','macro_f1_difference','promotion']}),flush=True)
    for name,result in [('candidate',new),('incumbent',old)]:
        print(name,json.dumps({k:result[k] for k in ['accuracy','macro_f1','confusion_matrix','errors']}),flush=True)


if __name__=='__main__':
    main()
