# modular.py
#
# Developed by Liam McInroy


import numpy as np

from sklearn.base import BaseEstimator, ClassifierMixin

from estimators.models.bayesian import BayesNet
from estimators.models.hmm import HMM


class ModularEstimator(BaseEstimator, ClassifierMixin):
    """This class uses a variety of other estimators on separate feature tables
    and then puts their estimations through another estimator to produce a
    single output
    """

    def __init__(self, cum_estimator=BayesNet,
                 ind_estimators=HMM, support=None,
                 sequential_data=False, modules_support=None, verbose=0):
        """Initializes a new modular framework. The cum_estimator will train
        on the outputs of the estimators from each other table. ind_estimators
        can either be a single type that will be initialized for each given
        table or a list of different estimators to use on each table

        Arguments:
            cum_estimator: The estimator trained on output from estimators
                from all of the given tables
            ind_estimators: A single type or array of type to use for each
                table
            support: The tuple of features to use within each individual
                estimator (if none then all)
            sequential_data: Whether the data passed is sequential or not
            modules_support: The way to split the features into different
                modules. If none, then it is assumed data passed is tupled
            verbose: The amount of output to give during training
        """
        self.modular = True
        self.sequential_data = sequential_data
        self.cum_estimator = cum_estimator
        self.current_cum_estimator = cum_estimator()
        self.ind_estimators = ind_estimators
        self.current_ind_estimators = []
        self.support = support
        self.modules_support = modules_support
        self.verbose = verbose

    def fit(self, X, y=None):
        """Fits each individual estimator and the cumulative estimator to
        the given data.

        Arguments:
            X: The input feature tables in a tuple where the last element
                is the correct label and the first is the sequence ID.
                It is implicitly assumed that each table is ordered by the
                sequence id (ascending). If self.modules_support is not None,
                then the single dataset X is split into modules according to
                self.modules_support
            y: The labels to each point in X. Only used if self.modules_support
                is not None.
        """
        X = self._reorganizeX(X, y)

        if self.support is not None:
            assert(len(X) == len(self.support))
        else:
            self.support = [None for _ in range(len(X))]

        if callable(self.ind_estimators):
            self.current_ind_estimators = [self.ind_estimators(
                                                support=self.support[i])
                                           for i in range(len(X))]
        else:
            assert(len(self.ind_estimators) == len(X))
            self.current_ind_estimators = \
                [init(support=self.support[i])
                 for i, init in enumerate(self.ind_estimators)]

        for i, x in enumerate(X):
            if not self.sequential_data or \
                    hasattr(self.current_ind_estimators[i], 'sequential'):
                self.current_ind_estimators[i].fit(x[:, :-1],
                                                   x[:, -1])
            else:
                self.current_ind_estimators[i].fit(x[:, 1:-1],
                                                   x[:, -1])
        self.support = [ind.support for ind in self.current_ind_estimators]

        self.current_cum_estimator = self.cum_estimator().fit(
                *self._get_ind_mle(X, y if y is not None else 1))

        if self.verbose == 1:
            print('Cumulative estimator support:',
                  self.current_cum_estimator.support)

        return self

    def predict(self, X, y=None):
        """Yields a prediction for a given set of data

        Arguments:
            X: The input feature tables as described in self.fit
            y: The labels
        """
        X = self._reorganizeX(X)

        return self.current_cum_estimator.predict(self._get_ind_mle(X))

    def predict_proba(self, X, y=None):
        """Yields the outcome probability for a given set of data

        Arguments:
            X: The input feature tables as described in self.fit
            y: The labels
        """
        X = self._reorganizeX(X)

        return self.current_cum_estimator.predict_proba(
                self._get_ind_mle(X))

    def score(self, X, y=None):
        """Yields a prediction for a given set of data and scores it

        Arguments:
            X: The input feature tables as described in self.fit
            y: The labels
        """
        raise NotImplementedError()

    def _get_ind_mle(self, X, y=None):
        X = self._reorganizeX(X, y)

        table_pids = [set(np.unique(x[:, 0])) for x in X]
        pids = list(set.union(*table_pids))

        if y is not None:
            y_ = []
        X_ = []
        if self.sequential_data:
            for pid in pids:
                arr = []
                if y is not None:
                    y_.append(None)
                for i, t_pids in enumerate(table_pids):
                    if pid in t_pids:
                        indices, = np.where(X[i][:, 0] == pid)
                        arr.append(np.atleast_2d(X[i][indices]))
                        if y is not None:
                            y_[-1] = X[i][indices[-1], -1]
                    else:
                        arr.append(np.full(X[i][0].shape, None))
                X_.append(arr)
        else:
            for i in range(X[0].shape[0]):
                arr = []
                for k in range(len(X)):
                    arr.append(np.atleast_2d(X[k][i]))
                    if y is not None and k == 0:
                        y_.append(X[k][i, -1])
                X_.append(arr)

        X_preds = []
        for x in np.array(X_):
            X_preds.append([])
            for i in range(len(self.current_ind_estimators)):
                if not self.sequential_data or \
                        hasattr(self.current_ind_estimators[i], 'sequential'):
                    X_preds[-1].append(
                            self.current_ind_estimators[i].predict(
                                x[i][:, :-1])[-1][-1])
                else:
                    X_preds[-1].append(
                            self.current_ind_estimators[i].predict(
                                x[i][:, 1:-1])[-1][-1])

        if y is None:
            return np.array(X_preds)
        else:
            return np.array(X_preds), np.array(y_)

    def _get_ind_preds(self, X, y=None):
        X = self._reorganizeX(X, y)

        table_pids = [set(np.unique(x[:, 0])) for x in X]
        pids = list(set.union(*table_pids))

        if y is not None:
            y_ = []
        X_ = []
        if self.sequential_data:
            for pid in pids:
                arr = []
                if y is not None:
                    y_.append(None)
                for i, t_pids in enumerate(table_pids):
                    if pid in t_pids:
                        indices, = np.where(X[i][:, 0] == pid)
                        arr.append(np.atleast_2d(X[i][indices]))
                        if y is not None:
                            y_[-1] = X[i][indices[-1], -1]
                    else:
                        arr.append(np.full(X[i][0].shape, None))
                X_.append(arr)
        else:
            for i in range(X[0].shape[0]):
                arr = []
                for k in range(len(X)):
                    arr.append(np.atleast_2d(X[k][i]))
                    if y is not None and k == 0:
                        y_.append(X[k][i, -1])
                X_.append(arr)

        X_preds = []
        for x in np.array(X_):
            X_preds.append({})
            for i in range(len(self.current_ind_estimators)):
                if not self.sequential_data or \
                        hasattr(self.current_ind_estimators[i], 'sequential'):
                    X_preds[-1][str(i)] = \
                            self.current_ind_estimators[i].predict_proba(
                                x[i][:, :-1])[-1][-1]
                else:
                    X_preds[-1][str(i)] = \
                            self.current_ind_estimators[i].predict_proba(
                                x[i][:, 1:-1])[-1][-1]

        if y is None:
            return np.array(X_preds)
        else:
            return np.array(X_preds), np.array(y_)

    def _reorganizeX(self, X, y=None):
        if not isinstance(X, tuple):
            if y is not None:
                return tuple(np.hstack((self.atleast_2d(X[:, supp]),
                                        y.reshape(-1, 1)))
                             for supp in self.modules_support)
            else:
                return tuple(np.hstack((self.atleast_2d(X[:, supp]),
                                        np.full((X.shape[0], 1), None)))
                             for supp in self.modules_support)
        return X

    def atleast_2d(self, arr):
        arr2 = np.atleast_2d(arr)
        if arr2.shape[0] == 1:
            return arr2.reshape(-1, 1)
        return arr2


def ModularGenerator(name='ModularGen', cum_estimator=BayesNet,
                     ind_estimators=HMM, supp=None, verb=0,
                     sequential_data=False, modules_support=None):
    def __init__(self, support=supp):
        return ModularEstimator.__init__(self, cum_estimator=cum_estimator,
                                         ind_estimators=ind_estimators,
                                         support=support,
                                         sequential_data=sequential_data,
                                         modules_support=modules_support,
                                         verbose=verb)
    return type(name, (ModularEstimator,), {'__init__': __init__})
