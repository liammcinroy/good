# hmm.py
#
# Developed by Liam McInroy


import numpy as np

from pomegranate import DiscreteDistribution, HiddenMarkovModel

from sklearn.base import BaseEstimator, ClassifierMixin

from estimators.models.bayesian import BayesNet


class HMM(BaseEstimator, ClassifierMixin):
    """This class uses a Hidden Markov Model which wraps around a given
    estimator and then performs prediction on the underlying hidden state
    """

    def __init__(self, estimator=BayesNet, support=None):
        """Initializes a new HMM. Since these are sequential, they require
        data which uses the first feature as a sequence id. Support is thus
        shifted accordingly. TODO: Change emissions to be estimator.predict?

        Arguments:
            estimator: The estimator CLASS to use within that is used as the
                measurement of the input before being put through the HMM
            support: The features to use. If none, then all are used
        """
        self.sequential = True  # Set to mark that modular should pass the ids
        self.estimator = estimator
        self.support = support
        self.current_estimator = estimator(support)
        self.hmm = None

    def fit(self, X, y=None):
        """Fits the model

        Arguments:
            X: The training features. Assumes to have the PersonID/SequenceID
                in the first feature
            y: Labels
        """
        X = np.array(X)
        y = y.flatten()

        self.current_estimator = self.estimator(self.support).fit(X[:, 1:], y)

        new_X, new_y = self._convert_batch(X, y)
        self.hmm = HiddenMarkovModel.from_samples(DiscreteDistribution,
                                                  n_components=2,
                                                  X=new_X, labels=new_y)

        return self

    def predict(self, X, y=None):
        """Create a prediction for the states, but since supplied in a
        non time-seris format then returns a single list. TODO also ignores
        the predictions for future states that aren't an outcome

        Arguments:
            X: The input features set, not converted into a time series set
            y: The labels for those features
        """
        return np.vstack([[1 if np.random.rand() < p else 0
                           for p in self.hmm.predict_proba(x)[:, 1]]
                          for x in self._convert_batch(X)])

    def predict_proba(self, X, y=None):
        """Returns the probability of the label being good

        Arguments:
            X: The input features set, not converted into a time series set
            y: The labels for those features
        """
        return np.vstack([self.hmm.predict_proba(x)[:, 1]
                          for x in self._convert_batch(X)])

    def score(self, X, y=None):
        """
        """
        raise NotImplementedError()

    def _convert_batch(self, X, y=None):
        """Converts a batch to a time series that can be used with a hmm

        Arguments:
            X: The input batch features, not yet sorted into time series
            y: The labels if need be
        """
        if y is not None:
            new_X = []
            new_y = []
            current_id = X[0, 0]
            current_seq = []
            current_seq_y = []
            for i, row in enumerate(X):
                if row[0] == current_id:
                    current_seq.append(
                        self._convert_obs(row, self.current_estimator.predict(
                            np.array([row[1:]]))))
                    current_seq_y.append(y[i])
                else:
                    new_X.append(current_seq)
                    new_y.append(current_seq_y)
                    current_id = row[0]
                    current_seq = \
                        [self._convert_obs(row, self.current_estimator.predict(
                            np.array([row[1:]])))]
                    current_seq_y = [y[i]]
            new_X.append(current_seq)
            new_y.append(current_seq_y)

            return np.array(new_X), np.array(new_y)

        else:
            new_X = []
            current_id = X[0, 0]
            current_seq = []
            for i, row in enumerate(X):
                if row[0] == current_id:
                    current_seq.append(
                        self._convert_obs(row, self.current_estimator.predict(
                            np.array([row[1:]]))))
                else:
                    new_X.append(current_seq)
                    current_id = row[0]
                    current_seq = \
                        [self._convert_obs(row, self.current_estimator.predict(
                            np.array([row[1:]])))]
            new_X.append(current_seq)

            return new_X

    def _convert_obs(self, X, y):
        """Converts a single observation to its hmm state index

        Arguments:
            X: The input features for a single observation
            y: The predicted value from the model
        """
        return 1 if y[0] == 1 else 0


def HMMGenerator(name='HMMGen', estimator=BayesNet):
    def __init__(self, support=None):
        return HMM.__init__(self, estimator=estimator, support=support)
    return type(name, (HMM,), {'__init__': __init__})
