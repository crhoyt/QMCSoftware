from ._stopping_criterion import StoppingCriterion
from ..accumulate_data import MLQMCData
from ..discrete_distribution import Lattice
from ..true_measure import Gaussian
from ..integrand import MLCallOptions
from ..util import MaxSamplesWarning, ParameterError
from numpy import argmax, sqrt
from scipy.stats import norm
from time import time
import warnings


class CubQMCML(StoppingCriterion):
    """
    Stopping criterion based on multi-level quasi-monte carlo

    >>> mlco = MLCallOptions(Gaussian(Lattice(seed=7)))
    >>> sc = CubQMCML(mlco,abs_tol=.05)
    >>> solution,data = sc.integrate()
    >>> solution
    10.444567069452214
    >>> data
    Solution: 10.4446
    MLCallOptions (Integrand Object)
        option          european
        sigma           0.200
        k               100
        r               0.050
        t               1
        b               85
    Lattice (DiscreteDistribution Object)
        dimension       2^(6)
        randomize       1
        seed            854306
        backend         gail
        mimics          StdUniform
    Gaussian (TrueMeasure Object)
        mean            0
        covariance      1
    CubQMCML (StoppingCriterion Object)
        rmse_tol        0.019
        n_init          2^(8)
        n_max           10000000000
        replications    2^(5)
    MLQMCData (AccumulateData Object)
        levels          7
        n_level         [4096.  256.  256.  256.  256.  256.  256.]
        mean_level      [1.006e+01 1.836e-01 1.029e-01 5.410e-02 2.773e-02 1.394e-02 6.967e-03]
        var_level       [6.143e-05 6.105e-05 4.080e-05 6.780e-06 3.139e-06 9.989e-07 4.290e-07]
        bias_estimate   0.007
        n_total         180224
        time_integrate  ...

    Reference:
        M.B. Giles and B.J. Waterhouse. 'Multilevel quasi-Monte Carlo path simulation'.
        pp.165-181 in Advanced Financial Modelling, in Radon Series on Computational and Applied Mathematics,
        de Gruyter, 2009. http://people.maths.ox.ac.uk/~gilesm/files/radon.pdf
    """

    parameters = ['rmse_tol','n_init','n_max','replications']

    def __init__(self, integrand, abs_tol=.05, alpha=.01, rmse_tol=None, n_init=256., n_max=1e10, replications=32.):
        """
        Args:
            integrand (Integrand): integrand with multi-level g method
            abs_tol (float): absolute tolerance
            alpha (float): uncertainty level
            rmse_tol (float): root mean squared error
                If supplied (not None), then absolute tolerance and alpha are ignored
                in favor of the rmse tolerance
            n_max (int): maximum number of samples
            replications (int): number of replications on each level
        """
        # initialization
        self.rmse_tol = float(rmse_tol) if rmse_tol else (float(abs_tol) / norm.ppf(1-alpha/2))
        self.n_init = float(n_init)
        self.n_max = float(n_max)
        self.replications = float(replications)
        # Verify Compliant Construction
        distribution = integrand.measure.distribution
        allowed_levels = 'multi'
        allowed_distribs = ["Lattice", "Sobol"]
        super(CubQMCML,self).__init__(distribution, allowed_levels, allowed_distribs)
        # Construct AccumulateData Object to House Integration Data
        self.data = MLQMCData(self, integrand, self.n_init, self.replications)

    def integrate(self):
        """ See abstract method. """
        t_start = time()
        while True:
            self.data.update_data()
            self.data.eval_level[:] = False
            if self.data.var_level.sum() > (self.rmse_tol**2/2.):
                # double N_l on level with largest V_l/(2^l*N_l)
                efficient_level = argmax(self.data.cost_level)
                self.data.eval_level[efficient_level] = True
            elif self.data.bias_estimate > (self.rmse_tol/sqrt(2.)):
                # add another level
                self.data.add_level()
            else:
                # both conditions met
                break
            total_next_samples = (self.data.replications*self.data.eval_level*self.data.n_level*2).sum()
            if (self.data.n_total + total_next_samples) > self.n_max:
                warning_s = """
                Alread generated %d samples.
                Trying to generate %d new samples, which would exceed n_max = %d.
                Stopping integration process.
                Note that error tolerances may no longer be satisfied""" \
                % (int(self.data.n_total), int(total_next_samples), int(self.n_max))
                warnings.warn(warning_s, MaxSamplesWarning)
                break
        self.data.time_integrate = time() - t_start
        return self.data.solution,self.data
