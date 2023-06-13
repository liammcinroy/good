# bayesian.py
#
# Developed by Liam McInroy


import numpy as np

import networkx as nx

from pomegranate import BayesianNetwork

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.metrics import accuracy_score


class BayesNet(BaseEstimator, ClassifierMixin):
    """This class is a wrapper for a pomagranate BayesianNetwork classifier.
    It will learn the structure of the network
    """

    def __init__(self, support=None):
        """Initializes the bayes net. If default is passed, then all features
        are used.

        Arguments:
            support: The feature indices to use in the model (after
                provided with all of them). If None, then it uses all features
        """
        self.support = support
        self.model = None
        self.known_cls = None

    def fit(self, X, y=None):
        """Fits the model to the given data using UniformDistributions

        Arguments:
            X: The dataset features to train on
            y: The labels
        """
        X = np.array(X).astype(str)
        y = y.reshape(-1, 1)

        features_node = tuple(np.arange(X.shape[1]) if self.support is None
                              else np.arange(len(self.support)))
        outputs_node = tuple([X.shape[1] if self.support is None
                              else len(self.support)])
        constraint_graph = nx.DiGraph([(features_node,
                                        outputs_node)])

        if self.support is not None:
            self.known_cls = {s_idx: np.unique(X[:, s_idx]).tolist()
                              for s_idx in self.support}
            X = self._preprocess_obs(np.array(X).astype(str))
            self.model = BayesianNetwork.from_samples(
                    np.hstack((X[:, self.support], y)),
                    algorithm='exact', constraint_graph=constraint_graph)
        else:
            self.known_cls = {j: np.unique(X[:, j]).tolist()
                              for j in range(X.shape[1])}
            X = self._preprocess_obs(np.array(X).astype(str))
            self.model = BayesianNetwork.from_samples(
                    np.hstack((X, y)),
                    algorithm='exact', constraint_graph=constraint_graph)

        return self

    def predict(self, X, y=None):
        """Uses the model to predict for a set

        Arguments:
            X: The dataset features to predict on
            y: The labels
        """
        X = self._preprocess_obs(np.array(X).astype(str))
        if self.support is not None:
            preds = self.model.predict(np.hstack((X[:, self.support],
                                                  np.full((len(X), 1), None))))
            return np.array([pred[-1]
                             for pred in preds]).reshape(-1, 1).astype(int)
        else:
            preds = self.model.predict(np.hstack((X,
                                                  np.full((len(X), 1), None))))
            return np.array([pred[-1]
                             for pred in preds]).reshape(-1, 1).astype(int)

    def predict_proba(self, X, y=None):
        """Uses the model to get the probability of class 1 over
        query variables (y) given the evidence (X)

        Arguments:
            X: The dataset features to predict probs on
            y: The labels
        """
        X = self._preprocess_obs(np.array(X).astype(str))
        if self.support is not None:
            preds = self.model.predict_proba(np.hstack((X[:, self.support],
                                                        np.full((len(X), 1),
                                                                None))))
            return np.array([pred[-1].probability('1')
                             for pred in preds]).reshape(-1, 1)
        else:
            preds = self.model.predict_proba(np.hstack((X,
                                                        np.full((len(X), 1),
                                                                None))))
            return np.array([pred[-1].probability('1')
                             for pred in preds]).reshape(-1, 1)

    def score(self, X, y=None):
        """Gets the current accuracy of the net

        Arguments:
            X: The dataset features to predict on
            y: The labels
        """
        return accuracy_score(y, self.predict(X))

    def _preprocess_obs(self, X):
        if isinstance(X, np.ndarray):
            X_ = X.astype(object)
            for j in range(X.shape[1]):
                if j in self.known_cls:
                    for i in range(X.shape[0]):
                        if X[i, j] not in self.known_cls[j]:
                            X_[i, j] = None
                        else:
                            X_[i, j] = str(self.known_cls[j].index(X[i, j]))
            return X_
        return X
