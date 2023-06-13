# neural.py
#
# Developed by Liam McInroy


import numpy as np

from keras.models import clone_model

from sklearn.base import BaseEstimator, ClassifierMixin


class NeuralNet(BaseEstimator, ClassifierMixin):
    """A sklearn wrapper for a keras network
    """

    def __init__(self, model=None, epochs=None, batch_size=None):
        """Initializes a new arbitrary keras network and uses it. Should
        already be compiled.

        Arguments:
            model: The keras.models.Sequential to be used. Make sure it has
                had compile called prior to passing
            epochs: The number of epochs to train on
            batch_size: The batch size to use during training
        """
        self.model = clone_model(model)
        self.model.set_weights(model.get_weights())
        self.model.compile(loss=model.loss, optimizer=model.optimizer,
                           metrics=model.metrics,
                           loss_weights=model.loss_weights,
                           sample_weight_mode=model.sample_weight_mode,
                           weighted_metrics=model.weighted_metrics)

        self.epochs = epochs
        self.batch_size = batch_size

    def fit(self, X, y=None):
        """Fit the keras model to X, y

        Arguments:
            X: The features of the dataset
            y: The corresponding labels
        """
        self.model.fit(X, y, epochs=self.epochs, batch_size=self.batch_size,
                       verbose=0)

        return self

    def predict(self, X, y=None):
        """Predicts using the keras model on X

        Arguments:
            X: The features of the set to predict on
        """
        return self.model.predict_on_batch(X)

    def predict_proba(self, X, y=None):
        """Predicts the probabilities using the keras model on X.
        When using a generator, then sampling is done (since this is
        a classifier) so this gives the raw probabilities

        Arguments:
            X: The features of the dataset to get probability classes for
        """
        return self.model.predict_on_batch(X)

    def score(self, X, y=None):
        """Scores the model using keras

        Arguments:
            X: The features of the set to test on
            y: The corresponding labels
        """
        return self.model.evaluate(X, y)

    def loss(self, X, y=None):
        """Gets the loss metric

        Arguments:
            X: The features of the set to test on
            y: The corresponding labels
        """
        return self.model.evaluate(X, y)


def NeuralNetGenerator(name, old, supp=None):
    """This method is a clever way to generate copies of a specific NeuralNet
    model with different features, used like:

    NewNetType = NeuralNetGenerator('NewNetType', old_neural_net)
    new_net = NewNetType([0, 3])

    Arguments:
        name: The string version of the new class name
        old: The old NeuralNet which the clones will be based on
    """

    def __init__(self, support=supp):
        """An initializer which uses the old instance's model to generate
        new versions with a support variable

        Arguments:
            support: A list of feature indices to use. If None,
                then all features are used.
        """
        setattr(self, 'support', support)
        type(old).__init__(self, old.model, old.epochs, old.batch_size)

    def fit(self, X, y=None):
        """Overloads so that support is used

        Arguments:
            X: The dataset features to train on
            y: labels
        """
        X = np.array(X)

        if self.support is not None:
            new_X = np.zeros(X.shape)
            new_X[:, self.support] = X[:, self.support]
            self.model.fit(new_X, y, epochs=self.epochs,
                           batch_size=self.batch_size, verbose=0)
        else:
            self.model.fit(X, y, epochs=self.epochs,
                           batch_size=self.batch_size, verbose=0)

        return self

    def predict(self, X, y=None):
        """Simply overloads so that support can be used.
        Also since we are dealing with classification problems, then
        it randomly samples a solution using the distribution given.

        Arguments:
            X: The set of features to predict on (unfiltered)
            y: The labels
        """
        X = np.array(X)

        dists = None
        if self.support is not None:
            new_X = np.zeros(X.shape)
            new_X[:, self.support] = X[:, self.support]
            dists = self.model.predict_on_batch(new_X)
        else:
            dists = self.model.predict_on_batch(X)

        preds = np.zeros_like(dists, dtype=int)
        for i, prob in enumerate(dists):
            preds[i] = 1 if np.random.random() < prob else 0
        return preds

    def predict_proba(self, X, y=None):
        """Overloads so self.support can be used

        Arguments:
            X: the set of features to predict on
            y: The labels
        """
        if self.support is not None:
            new_X = np.zeros(X.shape)
            new_X[:, self.support] = X[:, self.support]
            return self.model.predict_on_batch(new_X)
        else:
            return self.model.predict_on_batch(X)

    def score(self, X, y=None):
        """Overloads for use with support

        Arguments:
            X: The test dataset features
            y: The labels
        """
        X = np.array(X)

        if self.support is not None:
            new_X = np.zeros(X.shape)
            new_X[:, self.support] = X[:, self.support]
            return self.model.evaluate(new_X, y)
        else:
            return self.model.evaluate(X, y)

    def loss(self, X, y=None):
        """Overloads for use with support

        Arguments:
            X: The test dataset features
            y: The labels
        """
        X = np.array(X)

        if self.support is not None:
            new_X = np.zeros(X.shape)
            new_X[:, self.support] = X[:, self.support]
            return self.model.evaluate(new_X, y)
        else:
            return self.model.evaluate(X, y)

    return type(name, (NeuralNet,), {'__init__': __init__, 'fit': fit,
                                     'predict': predict,
                                     'predict_proba': predict_proba,
                                     'score': score})
