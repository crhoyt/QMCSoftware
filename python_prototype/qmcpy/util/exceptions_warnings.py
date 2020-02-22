""" Exceptions and Warnings thrown by qmcpy """


class DimensionError(Exception):
    """
    Class for raising error about dimension
    """


class DistributionCompatibilityError(Exception):
    """
    Class for raising error about incompatible distribution
    """


class NotYetImplemented(Exception):
    """
    Class for raising error when a component has been implemented yet
    """


class TransformError(Exception):
    """
    Class for raising error about transforming function to accommodate \
    distribution
    """


class ParameterError(Exception):
    """
    Class for raising error about input parameters
    """


class DistributionGenerationError(Exception):
    """
    Class for raising error about parameter inputs
    to gen_dd_samples (method of a DiscreteDistribution)
    """


class MethodImplementationError(Exception):
    """
    Class for raising error when an abstract method has not been implemented
    in the child class.
    """

    def __init__(self, subclass, method_name):
        s_f = '%s must implement the %s method. See superclass for method description ' + \
            'and expected arguments / return values.'
        super().__init__(s_f % (type(subclass).__name__, method_name))


class DistributionGenerationWarnings(Warning):
    """
    Class for issuing warningssabout parameter inputs
    to gen_dd_samples (method of a DiscreteDistribution)
    """


class ParameterWarning(Warning):
    """
    Class for issuing warnings about unacceptable parameters
    """


class MaxSamplesWarning(Warning):
    """
    Class for issuing warning about using maximum number of data samples
    """