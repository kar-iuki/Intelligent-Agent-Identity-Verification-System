"""Policy and nonlinear-preprocessing contracts independent of measured accuracy."""
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml.decision_model import DecisionPolicyClassifier, QualityShapeTransformer


class Probabilities:
    classes_=np.array(['Rejected','Verified','Manual Review'])
    n_features_in_=6
    def predict_proba(self,x):
        return np.repeat([[.1,.55,.35]],len(x),axis=0)


class Native:
    def predict(self,x): return np.repeat('Manual Review',len(x))


class ImprovementTests(unittest.TestCase):
    def test_review_policy_changes_decision_without_changing_probability(self):
        model=DecisionPolicyClassifier(Probabilities(),verified_threshold=.6)
        x=np.zeros((1,6))
        self.assertEqual(model.predict(x)[0],'Manual Review')
        np.testing.assert_array_equal(model.predict_proba(x),[[.1,.55,.35]])

    def test_native_boundary_can_differ_from_probability_argmax(self):
        model=DecisionPolicyClassifier(Probabilities(),Native(),policy='native')
        self.assertEqual(model.predict(np.zeros((1,6)))[0],'Manual Review')

    def test_probability_column_order_and_margin(self):
        plain=DecisionPolicyClassifier(Probabilities())
        cautious=DecisionPolicyClassifier(Probabilities(),verified_margin=.3)
        x=np.zeros((1,6))
        self.assertEqual(plain.predict(x)[0],'Verified')
        self.assertEqual(cautious.predict(x)[0],'Manual Review')

    def test_quality_transform_preserves_identity_columns_and_fitted_state(self):
        rng=np.random.default_rng(42)
        train=rng.uniform(size=(100,6));test=rng.uniform(size=(20,6))
        transformer=QualityShapeTransformer().fit(train)
        lambdas=transformer.power_.lambdas_.copy()
        out=transformer.transform(test)
        self.assertEqual(out.shape,test.shape)
        np.testing.assert_array_equal(out[:,:3],test[:,:3])
        np.testing.assert_array_equal(transformer.power_.lambdas_,lambdas)
        self.assertTrue(np.isfinite(out).all())
        self.assertTrue(((out[:,3:]>=0)&(out[:,3:]<=1)).all())


if __name__=='__main__': unittest.main(verbosity=2)
