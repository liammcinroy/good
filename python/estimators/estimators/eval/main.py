# main.py
#
# Developed by Liam McInroy


import argparse

import numpy as np

from estimators.models.bayesian import BayesNet
from estimators.models.evaluator import ModelEvaluator
from estimators.models.cvm import CVMGenerator
from estimators.models.dummy import DummyGenerator
from estimators.models.feature_selection import FeatureSelectionPipeline
from estimators.models.mim import MIMGenerator
from estimators.models.modular import ModularGenerator
from estimators.models.search import (
    SimulatedAnnealingFeatureSearch,
    GeneticFeatureSearch,
    MIMnFeatureSearch
)


def parse_args():
    parser = argparse.ArgumentParser(
        description='A simple script to evaluate a variety of models on a '
                    'binary classification task for feature selection.')
    parser.add_argument('dataset', type=str,
                        help='The path pointing to the dataset csv')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Whether to test all selected models.')
    parser.add_argument('--models', nargs='+', type=str,
                        help='The keys for the models to be tested.')
    return parser.parse_args()


def main():

    models = {
        'cvm': CVMGenerator(),
        'dummy': DummyGenerator,
        'bayes': BayesNet,
        'mim': MIMGenerator(),
        'cvm_bayes': CVMGenerator(estimator=BayesNet),
        'mim_bayes': MIMGenerator(estimator=BayesNet, n=5),
        'annealing_bayes': FeatureSelectionPipeline(
            SimulatedAnnealingFeatureSearch(BayesNet, iterations=20)),
        'genetic_bayes': FeatureSelectionPipeline(
            GeneticFeatureSearch(BayesNet, population=30, generations=100)),
        'genetic_mim_bayes': FeatureSelectionPipeline(
            GeneticFeatureSearch(MIMGenerator(estimator=BayesNet),
                                 population=20, generations=20)),
        'exhaustive_mim_bayes': FeatureSelectionPipeline(
            MIMnFeatureSearch(estimator=BayesNet, min_n=3, max_n=10)),
        }

    args = parse_args()

    train_models = models
    if not args.all:
        train_models = {model_name: models[model_name]
                        for model_name in args.models}

    dataset = np.genfromtxt(args.dataset, delimiter=',', dtype=int)
    X = dataset[:, 0:-1]
    y = dataset[:, -1].reshape(-1, 1)

    model_evaluator = ModelEvaluator(train_models, X, y)

    training_data = {model_name: (model_name,)
                     for model_name, _ in train_models.items()}

    for i, fold_results in enumerate(model_evaluator.run(len(X) - 1)):
        print('\tFold finished. Results:')
        print(fold_results)
        print()

        if i < 5:
            for model_name, _ in train_models.items():
                training_data[model_name] += fold_results[0][model_name]

    print('Cross validation done! Saving training data to train_dat.csv')
    train_dat_dump = np.full((len(train_models), 11),
                             None,
                             dtype=object)

    for i, (model_name, model_data) in enumerate(training_data.items()):
        for j, elem in enumerate(model_data):
            train_dat_dump[i, j] = elem

    np.savetxt('train_dat.csv', train_dat_dump, delimiter=',', fmt='%s')

    return


if __name__ == '__main__':
    main()
