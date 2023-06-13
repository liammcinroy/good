# mim.py
#
# Developed by Liam McInroy


import numpy as np


from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


class MIM(BaseEstimator, ClassifierMixin):
    """This model takes maximally the n features with the most mutual
    information with the class and then trains a logistic regression with them
    """

    def __init__(self, estimator=LogisticRegression, support=None, n=5):
        """Initialize a new MIM. Then self.support will
        remain as initialized and be replaced by a subset which contains
        (at most) the n features with the highest mutual information values.
        A logistic regression will then be used on those variables (unless a
        different class is provided)

        Arguments:
            estimator: The model CLASS to be used after feature selection
                is done
            support: The features to consider intially. Only a
                subset of this list will be chosen. If None, then all are used
            n: The n features with the highest mutual informations to return
        """
        self.support = support
        self.n = n
        self.estimator = estimator
        self.current_estimator = estimator()

    def fit(self, X, y=None):
        """Choose the statistically significant features and then trains
        a logistic regression on them

        Arguments:
            X: The training dataset
            y: The labels
        """

        if (self.support is not None and
                len(self.support) > self.n):
            mi = []
            for k in self.support:
                indices = np.where(X[:, k] != None)  # NOQA
                mi.append(mutual_info_classif(X[indices, k]
                                              .reshape(-1, 1)
                                              .astype(int),
                                              y[indices].astype(int))[0])
            self.support = self.support[np.argsort(-np.array(mi))[0:self.n]
                                        .tolist()]
        elif self.support is None:
            if self.n >= X.shape[1]:
                self.support = np.arange(X.shape[1]).tolist()
            else:
                mi = []
                for k in range(X.shape[1]):
                    indices = np.where(X[:, k] != None)  # NOQA
                    mi.append(mutual_info_classif(X[indices, k]
                                                  .reshape(-1, 1)
                                                  .astype(int),
                                                  y[indices].astype(int))[0])
                self.support = np.argsort(-np.array(mi))[0:self.n].tolist()

        if self.estimator is not LogisticRegression:
            self.current_estimator = self.estimator(self.support).fit(X, y)
        else:
            self.current_estimator = \
                LogisticRegression().fit(X[:, self.support].astype(int),
                                         y.astype(int))

        return self

    def predict(self, X, y=None):
        """Performs a prediction on X

        Arguments:
            X: The dataset features to predict for
            y: The labels
        """
        if self.estimator is not LogisticRegression:
            return self.current_estimator.predict(X)
        else:
            return self.current_estimator.predict(X[:, self.support])

    def score(self, X, y=None):
        """Evaluates the accuracy of the model

        Arguments:
            X: The dataset features to evaluate
            y: The labels
        """
        return accuracy_score(y, self.predict(X))


def MIMGenerator(name='MIMGen', estimator=LogisticRegression, n=5,
                 supp=None):
    def __init__(self, support=supp):
        MIM.__init__(self, estimator=estimator, support=support, n=n)
    return type(name, (MIM,), {'__init__': __init__})
