# search.py
#
# developed by Liam McInroy

import copy
from math import exp

import numpy as np

from genetic_selection import GeneticSelectionCV

from estimators.models.mim import MIM


class BaseFeatureSearcher:
    """An abstract class describing the inherited structure which any searcher
    should use for use in a FeatureSelectionPipeline
    """

    def __init__(self, estimator=None):
        """The initializer

        Arguments:
            estimator: The class of a particular model to fit for.
                Should have a support member and work in sklearn
        """
        self.estimator = estimator

        raise NotImplementedError()

    def search(self, X, y):
        """Method for discovering the next best feature subset

        Arguments:
            X: The dataset features to fit on
            y: The labels
        """
        raise NotImplementedError()


class SimulatedAnnealingFeatureSearch(BaseFeatureSearcher):
    """A simulated annealing search. Note that the neighbors could be
    more than just the addition/exclusion of a certain feature

    Also need to take another look at the acceptance function
    """

    def __init__(self, estimator=None, iterations=None):
        """Initialize a new annealing search

        Arguments:
            estimator: The class of a particular model to fit for.
                Should have a support member and work in sklearn
            iterations: The number of attempts for a given search
        """
        self.estimator = estimator
        self.iterations = iterations

    def search(self, X, y):
        """Method for discovering the next best feature subset

        Arguments:
            X: The dataset features to fit on
            y: The labels
        """
        n_features = len(X[0])

        full_features = set([x for x in range(n_features)])
        state_f = set(np.random.choice(n_features,
                                       np.random.randint(n_features),
                                       replace=False))

        state = self.estimator(list(state_f)).fit(X, y)
        state_score = self._energy(state, X, y, n_features)

        for k in range(1, self.iterations):
            T = k * 1. / self.iterations

            # choose new neighbor
            candidate_f = copy.deepcopy(state_f)

            candidates = list(full_features - state_f)
            addition = np.random.randint(len(candidates) + 1)
            if addition < len(candidates):
                candidate_f.add(candidates[addition])

            removal = np.random.randint(len(state_f) + 1)
            if removal < len(state_f):
                candidate_f.remove(state.support[removal])

            # test new neighbor
            candidate = self.estimator(list(candidate_f)).fit(X, y)
            candidate_score = self._energy(candidate, X, y, n_features)

            if (candidate_score > state_score or
                    np.random.rand(1) <
                    exp((candidate_score - state_score) / T)):
                state = candidate
                state_f = candidate_f
                state_score = candidate_score

        return state

    def _energy(self, estimator, X, y, n_features):
        return estimator.score(X, y) + \
               (n_features - len(estimator.support)) * .1 / n_features


class GeneticFeatureSearch(BaseFeatureSearcher):
    """This class uses a public source to perform a genetic search over the
    feature space.
    """

    def __init__(self, estimator=None, population=None,
                 generations=None, verbose=0):
        """The initializer.

        Arguments:
            estimator: The class of a particular model to fit for.
                Should have a support member and work in sklearn
            population: The number of models to have per generation
            generations: The number of generations to search for
        """
        self.estimator = estimator
        self.population = population
        self.generations = generations
        self.verbose = verbose

    def search(self, X, y):
        """Discovering the next best feature subset via genetic algorithms

        Arguments:
            X: The dataset features to fit on
            y: The labels
        """
        model = GeneticSelectionCV(self.estimator(), cv=10, scoring='accuracy',
                                   n_population=self.population,
                                   n_generations=self.generations,
                                   verbose=self.verbose).fit(X, y)
        support = [i for i, val in enumerate(model.support_) if val]

        return self.estimator(support).fit(X, y)


class MIMnFeatureSearch(BaseFeatureSearcher):
    """This class wraps around a MIM object and performs an exhaustive
    search over the n parameter
    """

    def __init__(self, estimator=None, min_n=None, max_n=None):
        """The initializer

        Arguments:
            estimator: The class of the model to fit for. It will be wrapped
                with a MIM
            min_n: The minimum n to test
            max_n: The maximum n to test
        """
        self.estimator = estimator
        self.min_n = min_n
        self.max_n = max_n

    def search(self, X, y):
        """Find the best value of n for a MIM object over the estimator

         Arguments:
            X: The dataset features to fit on
            y: The labels
        """
        best = MIM(estimator=self.estimator, n=self.min_n).fit(X, y)
        best_score = best.score(X, y)

        for n in range(self.min_n + 1, self.max_n + 1):
            candidate = MIM(estimator=self.estimator, n=n).fit(X, y)
            cand_score = candidate.score(X, y)

            if cand_score > best_score:
                best = candidate
                best_score = cand_score

        return best
