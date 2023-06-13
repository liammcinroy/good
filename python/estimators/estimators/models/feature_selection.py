# feature_selection.py
#
# Developed by Liam McInroy


from sklearn.base import BaseEstimator, ClassifierMixin


class FeatureSelectionPipeline(BaseEstimator, ClassifierMixin):
    """This class encapsulates the feature selection pipeline which takes
    a particular estimator model and a search technique to find the optimal
    feature set for the given estimator. Note that it requires the estimator
    to then be supplied as a class (inheriting sklearn.base.BaseEstimator) who
    accepts a list of indices for features to use. It should also have member
    'support' which saves this list
    """

    def __init__(self, searcher=None):
        """Initializes a new FeatureSelectionPipeline

        Arguments:
            searcher: An instance of a models.BaseSearcher
        """
        self.searcher = searcher
        self.current_estimator = None
        self.support = None

    def fit(self, X, y=None):
        """Runs the entire feature selection routine to conclusion
        and leaves the result in self.current_estimator.

        Note that successive calls are independent of one another

        Arguments:
            X: The features of the dataset
            y: The labels
        """

        self.current_estimator = self.searcher.search(X, y)
        self.support = self.current_estimator.support

        return self

    def predict(self, X, y=None):
        """Uses self.current_estimator to predict for the given set

        Arguments:
            X: The features for the set to test on (ALL OF THEM)
            y: The labels
        """

        return self.current_estimator.predict(X)

    def score(self, X, y=None):
        """Predicts and scores self.current_estimator on the given dataset

        Arguments:
            X: The features for the set to test on (ALL OF THEM)
            y: The labels
        """

        return self.current_estimator.score(X, y)

    def __call__(self):
        """Since we don't need to create a new instance (like with a network)
        when training then we can simply ignore a call
        """
        return self
