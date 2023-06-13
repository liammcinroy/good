# models.evaluator.py
# Class for evaluating many sklearn.base.ClassifierMixIn models
# Developed by Liam McInroy for DuoLogic, 6/27/2018


import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold
from sklearn.utils import check_X_y


class ModelEvaluator:
    """Class to evaluate multiple sklearn.base.ClassifierMixIn models
    on a binary classification task using LOO cross validation
    """

    def __init__(self, models, X, y):
        """Initializes a new ModelEvaluator

        Arguments:
            models: The dict of models (IN CLASSES so they can be initialized)
            X: The dataset features
            y: The dataset labels
        """
        self.models = models
        indices = np.arange(X.shape[0])
        np.random.shuffle(indices)
        self.X, self.y = check_X_y(X=X[indices], y=y[indices].flatten())

    def run(self, n_splits):
        """Iteratively runs the cross validation, returning all the models'
        scores after each successive fold

        Arguments:
            n_splits: The number of splits to use for cross validation
        """
        sk_k_fold = KFold(n_splits=n_splits)
        total_val_scores = {name: 0 for name, _ in self.models.items()}
        total_val_supp = {name: {i: 0 for i in range(self.X.shape[1])}
                          for name, _ in self.models.items()}
        for train_idx, test_idx in sk_k_fold.split(self.X, self.y):
            print('Beginning a new fold training cycle')

            train_X = self.X[train_idx]
            train_y = self.y[train_idx]
            test_X = self.X[test_idx]
            test_y = self.y[test_idx]

            val_scores = {}
            val_supports = {}
            for name, model in self.models.items():
                val_model = model().fit(train_X, train_y)
                val_scores[name] = (accuracy_score(train_y.astype(int),
                                                   val_model.predict(train_X)),
                                    accuracy_score(test_y.astype(int),
                                                   val_model.predict(test_X)))
                total_val_scores[name] += val_scores[name][1] / n_splits

                val_supports[name] = val_model.support
                if val_model.support is not None and \
                        isinstance(val_model.support[0], int):
                    for supp in val_model.support:
                        total_val_supp[name][supp] += 1. / n_splits

            yield val_scores, val_supports

        print("Finished cross validation.")
        yield total_val_scores, total_val_supp


class ModularModelEvaluator:
    """Class to evaluate multiple .models.modular.Modular models
    on a binary classification task using LOO cross validation
    """

    def __init__(self, models, X):
        """Initializes a new ModelEvaluator

        Arguments:
            models: The dict of models (IN CLASSES so they can be initialized)
            X: The dataset features
            y: The dataset labels
        """
        for model_name, model in models.items():
            assert(hasattr(model(), 'modular'))
        self.models = models
        self.X = tuple(x for x in X)
        self.table_pids = [set(np.unique(x[:, 0])) for x in X]
        self.pids = list(set.union(*self.table_pids))

    def run(self, n_splits):
        """Iteratively runs the cross validation, returning all the models'
        scores after each successive fold

        Arguments:
            n_splits: The number of splits to use for cross validation
        """
        sk_k_fold = KFold(n_splits=n_splits)
        total_val_scores = {name: 0 for name, _ in self.models.items()}
        total_val_supp = {name: [{j: 0 for j in range(x.shape[1] - 2)}
                                 for x in self.X]
                          for name, _ in self.models.items()}
        for train_pids_idx, test_pids_idx in sk_k_fold.split(self.pids):
            print('Beginning a new fold training cycle')

            train_X, train_y = self.get_data_with_id(
                    [self.pids[i] for i in train_pids_idx])
            test_X, test_y = self.get_data_with_id(
                    [self.pids[i] for i in test_pids_idx])

            val_scores = {}
            val_supports = {}
            for name, model in self.models.items():
                val_model = model().fit(train_X, train_y)
                val_scores[name] = (accuracy_score(train_y,
                                                   val_model.predict(train_X)),
                                    accuracy_score(test_y,
                                                   val_model.predict(test_X)))
                total_val_scores[name] += val_scores[name][1] / n_splits

                val_supports[name] = val_model.support
                for i, supp in enumerate(val_model.support):
                    if supp is not None:
                        for f_idx in supp:
                            total_val_supp[name][i][f_idx] += 1. / n_splits

            yield val_scores, val_supports

        print("Finished cross validation.")
        yield total_val_scores, total_val_supp

    def get_data_with_id(self, pids):
        """Returns the data in self.X matching the sequence IDs
        """
        X = []
        y = []
        for i, t_pids in enumerate(self.table_pids):
            arr = []
            for j, pid in enumerate(pids):
                y.append(None)
                if pid in t_pids:
                    indices, = np.where(self.X[i][:, 0] == pid)
                    arr.append(np.vstack(self.X[i][indices]).astype(object))
                    y[j] = self.X[i][indices[-1], -1]
                else:
                    dat = np.full(self.X[i][0].shape, None, dtype=None)
                    dat[0] = pid
                    arr.append(dat)
            X.append(np.vstack(arr).astype(object))

        for k in range(len(X)):
            X[k][np.where(X[k] == -1)] = None

        return tuple(x for x in X), np.array(y)
