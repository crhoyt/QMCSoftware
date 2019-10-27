""" Definition for CLTRep, a concrete implementation of StoppingCriterion """

from numpy import array, tile, zeros
from scipy.stats import norm

from . import StoppingCriterion
from ..accum_data import MeanVarDataRep
from .._util import MaxSamplesWarning


class CLTRep(StoppingCriterion):
    """ Stopping criterion based on var(stream_1_estimate, ..., stream_16_estimate) < errorTol """

    def __init__(self, discrete_distrib, true_measure,
                 replications=16, inflate=1.2, alpha=0.01,
                 abs_tol=1e-2, rel_tol=0,
                 n_init=1024, n_max=1e8):
        """
        Args:
            discrete_distrib
            true_measure (DiscreteDistribution): an instance of DiscreteDistribution
            replications (int): number of random nxm matrices to generate
            inflate (float): inflation factor when estimating variance
            alpha (float): significance level for confidence interval
            abs_tol (float): absolute error tolerance
            rel_tol (float): relative error tolerance
            n_init (int): initial number of samples
            n_max (int): maximum number of samples
        """
        allowed_distribs = ["Lattice", "Sobol"]  # supported distributions
        super().__init__(discrete_distrib, allowed_distribs, abs_tol,
                         rel_tol, n_init, n_max)
        self.inflate = inflate  # inflation factor
        self.alpha = alpha  # uncertainty level
        self.stage = "begin"
        # Construct Data Object
        n_integrands = len(true_measure)
        self.data = MeanVarDataRep(n_integrands, replications)
        #   house integration data
        self.data.n = tile(self.n_init,n_integrands)  # next n for each integrand
        self.data.n_total = zeros(n_integrands)

    def stop_yet(self):
        """ Determine when to stop """
        for i in range(self.data.n_integrands):
            if self.data.sighat[i] < self.abs_tol:
                # sufficient estimate for mean of f[i]
                self.data.flag[i] = 0  # Stop estimation of i_th f
                continue
            self.data.n[i] *= 2 # Double n for next sample
        if self.data.flag.sum() == 0:
            self.data.n_total = self.data.n.sum()
            err_bar = -norm.ppf(self.alpha / 2) * self.inflate \
                * (self.data.sighat ** 2 / self.data.n).sum(0) ** 0.5
            self.data.confid_int = self.data.solution + err_bar * array([-1, 1])  # CLT confidence interval
            self.stage = "done"  # finished with computation
