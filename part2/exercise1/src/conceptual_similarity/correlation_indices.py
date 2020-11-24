import numpy

def pearson_correlation_index(x, y):
    """
    Implementation of the Pearson index:
    Cov(X,Y)/σX * σY
    :param x: golden value
    :param y: similarity list
    :return: Pearson correlation index
    """
    mean_x = numpy.mean(x)
    mean_y = numpy.mean(y)

    deviations__x = [value - mean_x for value in x]
    deviations__y = [value - mean_y for value in y]

    covariance = numpy.mean(numpy.multiply(deviations__x, deviations__y))

    return covariance / numpy.std(x) * numpy.std(y)

def spearman_correlation_index(x, y):
    """
    Spearman index.
    :param x: first list
    :param y: second list
    :return: Spearman correlation index
    """
    return pearson_correlation_index(define_rank(x), define_rank(y))


def define_rank(values):
    """
    :param x: numeric vector
    :return: ranks list, sorted as the input order
    """
    values_w_rank = [(values[index], index) for index in range(len(values))]
    values_w_rank_sorted = sorted(values_w_rank, key=lambda x: x[0])
    return [rank for (_, rank) in values_w_rank_sorted]
