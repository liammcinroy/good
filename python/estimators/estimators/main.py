# main.py
#
# Developed by Liam McInroy


import argparse
import pickle

import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold

from pomegranate import BayesianNetwork

from estimators.models.bayesian import BayesNet
from estimators.models.feature_selection import FeatureSelectionPipeline
from estimators.models.modular import ModularGenerator
from estimators.models.search import MIMnFeatureSearch


# Change this based on the dataset supplied. Should cover all the features
# which are being considered (in the joint table)
MODULES_SUPPORT = list(range(2, 41))

TRAIN_MODEL_T = ModularGenerator(
        cum_estimator=FeatureSelectionPipeline(
           MIMnFeatureSearch(estimator=BayesNet, min_n=5, max_n=15)),
        ind_estimators=BayesNet, modules_support=MODULES_SUPPORT)

# Change this based on the number of cross validation folds desired.
# I suggest leave one out cross validation, so change to the number of
# datapoints minus one
POPULATION_N = 223


def select_features(**kwargs):
    """A method to select the most popular features from the population
    """
    data = kwargs.get('dataset')
    ind = np.arange(len(data))
    np.random.shuffle(ind)
    X = data[ind, :-1]
    y = data[ind, -1]

    feature_proba = {i: 0 for i in range(len(MODULES_SUPPORT))}

    acc = 0
    kfold = KFold(n_splits=POPULATION_N)
    for train_idx, test_idx in kfold.split(X, y):
        model = TRAIN_MODEL_T().fit(X[train_idx], y[train_idx])
        for s in model.cum_estimator.support:
            feature_proba[s] += 1. / POPULATION_N
        accT = accuracy_score(y[test_idx], model.predict(X[test_idx]))
        acc += accT

    if kwargs.get('verbose', False):
        print('Estimated accuracy: ', acc / POPULATION_N)

    if kwargs.get('verbose', False):
        print('The features probabilities:', feature_proba)

    #support = [s for i, s in enumerate(MODULES_SUPPORT)
    #           if np.random.rand() < feature_proba[i]]
    desc_prob_ind = np.argsort([-feature_proba[i]
                                for i in range(len(MODULES_SUPPORT))])
    support = desc_prob_ind[0:15]

    if kwargs.get('verbose', False):
        print('Support: ', support)

    return support


def train_final_model(support, **kwargs):
    data = kwargs.get('dataset')
    X = data[:, :-1]
    y = data[:, -1]
    
    if kwargs.get('verbose', False):
        loo = LeaveOneOut()
        acc = 0
        for train, test in loo.split(X):
            acc += accuracy_score(y[test],
                BayesNet(support).fit(X[train], y[train]).predict(X[test]))
        print('Estimated accuracy of final model:', acc / (len(X) - 1))

    model = BayesNet(support)
    return model.fit(X, y)


def save_final_model(model, **kwargs):
    save_data = {'json': model.model.to_json(),
                 'support': model.support,
                 'known_cls': model.known_cls}
    with open(kwargs.get('model_path'), 'wb') as f:
        pickle.dump(save_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_final_model(**kwargs):
    with open(kwargs.get('model_path'), 'rb') as f:
        load_data = pickle.load(f)
    support = load_data.pop('support')

    if kwargs.get('verbose', False):
        print('Loaded support:', support)

    model = BayesNet(support)
    model.known_cls = load_data.pop('known_cls')
    model.model = BayesianNetwork.from_json(load_data.pop('json'))
    return model


def parse_args():
    parser = argparse.ArgumentParser(
            description='A command line interface to train a group of models '
                        'on a dataset to select the most important features, '
                        'then finally train a final model on those features '
                        'and save it.')
    parser.add_argument('mode', type=str,
                        help='The mode to run the program in. If "train" then'
                             ' the dataset_file must point to a file with '
                             'labels in it and the final model is saved to '
                             'model_path. If "test", then dataset_file must '
                             'point to a file with features only and the '
                             'predictions are outputted to the console based '
                             'on the model saved in model_path.')
    parser.add_argument('dataset_file', type=str,
                        help='The file (in a csv format) which the dataset '
                             'is within (based on the rules explained above).')
    parser.add_argument('model_path', type=str,
                        help='The file to save/load the model from dependent '
                             'on mode.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether to output data while training.'),
    parser.add_argument('-s', '--support', type=int, nargs='+',
                        help='The input support features to use instead.')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.mode == 'train':
        dataset = np.genfromtxt(args.dataset_file, delimiter=',', dtype=str)

        if args.support is None:
            support = select_features(dataset=dataset, **vars(args))
        else:
            support = args.support
        kwargs = vars(args)
        del kwargs['support']
        model = train_final_model(support, dataset=dataset, **kwargs)
        save_final_model(model, **vars(args))
    elif args.mode == 'test':
        model = load_final_model(**vars(args))
        predX = np.genfromtxt(args.dataset_file, delimiter=',', dtype=str)
        print(model.predict_proba(predX))
    return


if __name__ == '__main__':
    main()
