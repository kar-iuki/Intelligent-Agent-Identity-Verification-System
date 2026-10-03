"""Static validation-selected decision policy; probabilities remain unmodified."""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from sklearn.preprocessing import PowerTransformer, MinMaxScaler


class QualityShapeTransformer(TransformerMixin, BaseEstimator):
    """Learn quality skew corrections without changing the six-column order."""
    def fit(self, x, y=None):
        self.n_features_in_ = np.asarray(x).shape[1]
        self.power_ = PowerTransformer(standardize=False).fit(np.asarray(x)[:, 3:])
        self.scaler_ = MinMaxScaler(clip=True).fit(self.power_.transform(np.asarray(x)[:, 3:]))
        return self

    def transform(self, x):
        result = np.asarray(x, dtype=float).copy()
        result[:, 3:] = self.scaler_.transform(self.power_.transform(result[:, 3:]))
        return result


class DecisionPolicyClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, calibrated, native=None, policy='probability',
                 review_multiplier=1.0, verified_threshold=0.0, verified_margin=0.0):
        self.calibrated = calibrated
        self.native = native
        self.policy = policy
        self.review_multiplier = review_multiplier
        self.verified_threshold = verified_threshold
        self.verified_margin = verified_margin
        self.classes_ = calibrated.classes_
        self.n_features_in_ = calibrated.n_features_in_

    def __sklearn_is_fitted__(self):
        return True

    def fit(self, x, y=None):
        raise RuntimeError('This policy wraps frozen offline-trained estimators; run improve_model.py to train.')

    def predict_proba(self, x):
        return self.calibrated.predict_proba(x)

    def decide(self, probabilities):
        classes = list(self.classes_)
        review = classes.index('Manual Review')
        verified = classes.index('Verified')
        adjusted = np.asarray(probabilities).copy()
        adjusted[:, review] *= self.review_multiplier
        labels = self.classes_[np.argmax(adjusted, axis=1)].copy()
        runner_up = np.max(np.delete(probabilities, verified, axis=1), axis=1)
        uncertain = ((probabilities[:, verified] < self.verified_threshold) |
                     (probabilities[:, verified] - runner_up < self.verified_margin))
        labels[(labels == 'Verified') & uncertain] = 'Manual Review'
        return labels

    def predict(self, x):
        if self.policy == 'native':
            return self.native.predict(x)
        return self.decide(self.predict_proba(x))

    @property
    def decision_policy(self):
        return {'name': self.policy, 'review_multiplier': self.review_multiplier,
                'verified_threshold': self.verified_threshold, 'verified_margin': self.verified_margin}
