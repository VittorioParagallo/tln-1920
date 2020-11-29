import numpy
import pandas as pd
def pearson_correlation_index(_X, _Y):
    """
    Implementation of the Pearson index:
    Cov(X,Y)/σX * σY
    :param x: golden value
    :param y: similarity list
    :return: Pearson correlation index
    """
    X=numpy.array( _X)
    Y=numpy.array(_Y)
    ''' Compute Pearson Correlation Coefficient. '''
    # Normalise X and Y
    X -= X.mean(0)
    Y -= Y.mean(0)
    # Standardise X and Y
    X /= X.std(0)
    Y /= Y.std(0)
    # Compute mean product
    return numpy.mean(X*Y)

def spearman_correlation_index(x, y):
    """
    Spearman index.
    :param x: first list
    :param y: second list
    :return: Spearman correlation index
    """
    xranks = pd.Series(x).rank()
    yranks = pd.Series(y).rank()
    return pearson_correlation_index(xranks, yranks)
  