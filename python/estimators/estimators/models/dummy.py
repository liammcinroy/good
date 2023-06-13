# dummy.py
#
# Developed by Liam McInroy


from sklearn.dummy import DummyClassifier


def DummyGenerator(support=None):
    model = DummyClassifier(strategy='stratified')
    model.support = None
    return model
