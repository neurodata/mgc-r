import numpy as np
import math
from mgcpy.independence_tests.dcorr import DCorr
import scipy.io
import os


def power(independence_test, sample_generator, num_samples=100, num_dimensions=1, noise=0.0, repeats=1000, alpha=.05, simulation_type=''):
    '''
    Estimate the power of an independence test given a simulator to sample from

    :param independence_test: an object whose class inherits from the ``Independence_Test`` abstract class
    :type independence_test: ``Object(Independence_Test)``

    :param sample_generator: a function used to generate simulation from ``simulations`` with parameters given by the following arguments
        - ``num_samples``: default to 100
        - ``num_dimensions``: default to 1
        - ``noise``: default to 0
    :type sample_generator: ``FunctionType`` or ``callable()``

    :param num_samples: the number of samples generated by the simulation (default to 100)
    :type num_samples: int

    :param num_dimensions: the number of dimensions of the samples generated by the simulation (default to 1)
    :type num_dimensions: int

    :param noise: the noise used in simulation (default to 0)
    :type noise: float

    :param repeats: the number of times we generate new samples to estimate the null/alternative distribution (default to 1000)
    :type repeats: int

    :param alpha: the type I error level (default to 0.05)
    :type alpha: float

    :param simulation_type: specify simulation when necessary (default to empty string)
    :type simulation_type: string

    :return empirical_power: the estimated power
    :rtype: numpy.float

    **Example**

    >>> from mgcpy.benchmarks.power import power
    >>> from mgcpy.independence_tests.mgc.mgc import MGC
    >>> from mgcpy.benchmarks.simulations import circle_sim
    >>> mgc = MGC()
    >>> mgc_power = power(mgc, circle_sim, num_samples=100, num_dimensions=2, simulation_type='ellipse')
    '''

    # test statistics under the null, used to estimate the cutoff value under the null distribution
    test_stats_null = np.zeros(repeats)
    # test statistic under the alternative
    test_stats_alternative = np.zeros(repeats)
    for rep in range(repeats):
        # generate new samples for each iteration
        # the if-else block below is for simulations that have a different argument list
        # than the general case
        if simulation_type == 'sine_16pi':
            matrix_X, matrix_Y = sample_generator(num_samples, num_dimensions, noise=noise, period=np.pi*16)
        elif simulation_type == 'multi_noise' or simulation_type == 'multi_indept':
            matrix_X, matrix_Y = sample_generator(num_samples, num_dimensions)
        elif simulation_type == 'ellipse':
            matrix_X, matrix_Y = sample_generator(num_samples, num_dimensions, noise=noise, radius=5)
        elif simulation_type == 'diamond':
            matrix_X, matrix_Y = sample_generator(num_samples, num_dimensions, noise=noise, period=-np.pi/8)
        else:
            matrix_X, matrix_Y = sample_generator(num_samples, num_dimensions, noise=noise)

        # permutation test
        permuted_y = np.random.permutation(matrix_Y)
        test_stats_null[rep], _ = independence_test.test_statistic(matrix_X, permuted_y)
        test_stats_alternative[rep], _ = independence_test.test_statistic(matrix_X, matrix_Y)

        '''
        # if the test is pearson, use absolute value of the test statistic
        # so the more extreme test statistic is still in a one-sided interval
        if independence_test.get_name() == 'pearson':
            test_stats_null[rep] = abs(test_stats_null[rep])
            test_stats_alternative[rep] = abs(test_stats_alternative[rep])
        '''

    # the cutoff is determined so that 1-alpha of the test statistics under the null distribution
    # is less than the cutoff
    cutoff = np.sort(test_stats_null)[math.ceil(repeats*(1-alpha))]
    # the proportion of test statistics under the alternative which is no less than the cutoff (in which case
    # the null is rejected) is the empirical power
    empirical_power = np.where(test_stats_alternative >= cutoff)[0].shape[0] / repeats
    return empirical_power


def power_given_data(independence_test, simulation_type, data_type='dimension', num_samples=100, num_dimensions=1, repeats=1000, alpha=.05):
    '''
    Estimate the power of an independence test given pre-generated data from the repository ``MGC-paper``
    Mostly for internal testing purposes

    :param independence_test: an object whose class inherits from the ``Independence_Test`` abstract class
    :type independence_test: ``Object(Independence_Test)``

    :param simulation_type: specify which simulation is used
    :type simulation_type: int within ``[1, 20]``

    :param data_type: the pre-generated data is either increasing in dimensions or increasing in sample sizes
    :type data_type: string, either 'dimension' or 'sample_size'

    :param num_samples: the number of samples generated by the simulation (default to 100)
    :type num_samples: int

    :param num_dimensions: the number of dimensions of the samples generated by the simulation (default to 1)
    :type num_dimensions: int

    :param noise: the noise used in simulation (default to 0)
    :type noise: float

    :param repeats: the number of times we generate new samples to estimate the null/alternative distribution (default to 1000)
    :type repeats: int

    :param alpha: the type I error level (default to 0.05)
    :type alpha: float

    :return empirical_power: the estimated power
    :rtype: numpy.float

    **Example**

    >>> from mgcpy.benchmarks.power import power_given_data
    >>> from mgcpy.independence_tests.mgc.mgc import MGC
    >>> from mgcpy.benchmarks.simulations import circle_sim
    >>> mgc = MGC()
    >>> mgc_power = power_given_data(mgc, simulation_type=4, num_samples=100, num_dimensions=2)
    '''
    # test statistics under the null, used to estimate the cutoff value under the null distribution
    test_stats_null = np.zeros(repeats)
    # test statistic under the alternative
    test_stats_alternative = np.zeros(repeats)
    # absolute path to the benchmark directory
    dir_name = os.path.dirname(__file__)
    # load the relevant pre-generated data
    if data_type == 'dimension':
        file_name_prefix = dir_name + '/sample_data_power_dimensions/type_{}_dim_{}'.format(simulation_type, num_dimensions)
    else:
        file_name_prefix = dir_name + '/sample_data_power_sample_size/type_{}_size_{}'.format(simulation_type, num_samples)
    all_matrix_X = scipy.io.loadmat(file_name_prefix + '_X.mat')['X']
    all_matrix_Y = scipy.io.loadmat(file_name_prefix + '_Y.mat')['Y']
    for rep in range(repeats):
        matrix_X = all_matrix_X[:, :, rep]
        matrix_Y = all_matrix_Y[:, :, rep]
        # permutation test
        permuted_y = np.random.permutation(matrix_Y)
        test_stats_null[rep], _ = independence_test.test_statistic(matrix_X, permuted_y)
        test_stats_alternative[rep], _ = independence_test.test_statistic(matrix_X, matrix_Y)
        '''
        # if the test is pearson, use absolute value of the test statistic
        # so the more extreme test statistic is still in a one-sided interval
        if independence_test.get_name() == 'pearson':
            test_stats_null[rep] = abs(test_stats_null[rep])
            test_stats_alternative[rep] = abs(test_stats_alternative[rep])
        '''

    # the cutoff is determined so that 1-alpha of the test statistics under the null distribution
    # is less than the cutoff
    cutoff = np.sort(test_stats_null)[math.ceil(repeats*(1-alpha))]
    # the proportion of test statistics under the alternative which is no less than the cutoff (in which case
    # the null is rejected) is the empirical power
    empirical_power = np.where(test_stats_alternative >= cutoff)[0].shape[0] / repeats
    return empirical_power
