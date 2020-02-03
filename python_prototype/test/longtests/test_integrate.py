""" Unit tests for integrate method in QMCPy """

import unittest

from numpy import arange, array
from qmcpy import *


class IntegrationExampleTest(unittest.TestCase):

    def test_keister(self):
        """
        Mathematica:
        3D:  N[Integrate[E^(-x1^2 - x2^2 - x3^2) Cos[Sqrt[x1^2 + x2^2 + x3^2]], {x1, -Infinity, Infinity}, {x2, -Infinity, Infinity}, {x3, -Infinity, Infinity}]]
        2D:  N[Integrate[E^(-x1^2 - x2^2) Cos[Sqrt[x1^2 + x2^2]], {x1, -Infinity, Infinity}, {x2, -Infinity, Infinity}]]
        1D:  N[Integrate[E^(-x^2) Cos[Sqrt[x^2]], {x, -Infinity, Infinity}]]
        """
        abs_tol = 0.01
        dimensions = [1, 2, 3]
        true_values = [1.3803884470431430, 1.808186429263620, 2.168309102165481]
        for d in dimensions:
            integrand = Keister(dimension=d)
            distrib = IIDStdGaussian(rng_seed=7)
            measure = Gaussian(dimension=d, variance=1 / 2)
            stopping_criterion = CLT(distrib, measure,
                                     abs_tol=abs_tol)
            sol, _ = integrate(integrand, measure,
                               distrib, stopping_criterion)
            true_value = true_values[d - 1]
            self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_asian_option_multi_level(self):
        abstol = 0.1
        time_vec = [arange(1 / 4, 5 / 4, 1 / 4),
                    arange(1 / 16, 17 / 16, 1 / 16),
                    arange(1 / 64, 65 / 64, 1 / 64)]
        dims = [len(tv) for tv in time_vec]
        distrib = IIDStdGaussian(rng_seed=7)
        measure = BrownianMotion(dims, time_vector=time_vec)
        integrand = AsianCall(measure)
        stopping_criterion = CLT(distrib, measure, abs_tol=abstol)
        sol, _ = integrate(integrand, measure,
                           distrib, stopping_criterion)
        true_value = 6.20
        self.assertTrue(abs(sol - true_value) < abstol)

    def test_lebesgue_measure(self):
        """ Mathematica: Integrate[x^3 y^3, {x, 1, 3}, {y, 3, 6}] """
        abs_tol = 1
        dimension = 2
        integrand = QuickConstruct(dimension=dimension,
                                   custom_fun=lambda x: (x.prod(1)) ** 3)
        measure = Lebesgue(dimension=dimension,
                                lower_bound=[array([1, 3])],
                                upper_bound=[array([3, 6])])
        distrib = Lattice(rng_seed=7)
        stopping_criterion = CLTRep(distrib, measure,
                                    abs_tol=abs_tol)
        sol, _ = integrate(integrand, measure,
                           distrib, stopping_criterion)
        true_value = 6075
        self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_uniform_measure(self):
        """ Mathematica: Integrate[(x^3 y^3)/6, {x, 1, 3}, {y, 3, 6}] """
        abs_tol = 1
        dimension = 2
        integrand = QuickConstruct(dimension=dimension,
                                   custom_fun=lambda x: (x.prod(1)) ** 3)
        measure = Uniform(dimension=dimension,
                               lower_bound=[array([1, 3])],
                               upper_bound=[array([3, 6])])
        distrib = Lattice(rng_seed=7)
        stopping_criterion = CLTRep(distrib, measure,
                                    abs_tol=abs_tol)
        sol, _ = integrate(integrand, measure,
                           distrib, stopping_criterion)
        true_value = 6075 / 6
        self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_linear(self):
        """ Mathematica:
        1D: Integrate[x, {x, 0, 1}]
        2D: Integrate[x+y, {x, 0, 1}, {y, 0, 1}]
        3D: Integrate[x+y+z, {x, 0, 1}, {y, 0, 1}, {z, 0, 1}]
        """
        abs_tol = 0.01
        dimensions = [1, 2, 3]
        true_values = [0.5, 1, 1.5]
        for d in dimensions:
            integrand = Linear(dimension=d)
            measure = Uniform(dimension=d)
            distrib = IIDStdUniform(rng_seed=7)
            stopping_criterion = CLT(distrib, measure, abs_tol=abs_tol)
            sol, _ = integrate(integrand, measure, distrib,
                               stopping_criterion)
            true_value = true_values[d - 1]
            self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_quick_construct(self):
        """
        Infer true measure's dimension from integrand's

        Mathematica:
        1D: Integrate[5x, {x, 0, 1}]
        2D: Integrate[5(x+y), {x, 0, 1}, {y, 0, 1}]
        3D: Integrate[5(x+y+z), {x, 0, 1}, {y, 0, 1}, {z, 0, 1}]
        """

        def f(x): return (5 * x).sum(1)

        dimensions = [1, 2, 3]
        true_values = [2.5, 5, 7.5]
        for d in dimensions:
            integrand = QuickConstruct(dimension=d, custom_fun=f)
            measure = Uniform(dimension=d)
            sol, data = integrate(integrand, measure)
            print(data)
            abs_tol = data.stopping_criterion.abs_tol
            true_value = true_values[d - 1]
            self.assertTrue(data.measure.dimension == d)
            self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_quick_construct2(self):
        """
        Infer integrand dimension from true measure's

        Mathematica:
        1D: Integrate[5x, {x, 0, 1}]
        2D: Integrate[5(x+y), {x, 0, 1}, {y, 0, 1}]
        3D: Integrate[5(x+y+z), {x, 0, 1}, {y, 0, 1}, {z, 0, 1}]
        """

        def f(x): return (5 * x).sum(1)

        dimensions = [1, 2, 3]
        true_values = [2.5, 5, 7.5]
        for d in dimensions:
            integrand = QuickConstruct(dimension=d,
                                       custom_fun=f)
            measure = Uniform(dimension=d)
            sol, data = integrate(integrand, measure)
            print(data)
            abs_tol = data.stopping_criterion.abs_tol
            true_value = true_values[d - 1]
            self.assertTrue(measure.dimension == d)
            self.assertTrue(data.measure.dimension == d)
            self.assertTrue(abs(sol - true_value) < abs_tol)

    def test_quick_construct3(self):
        """
        Test integrands with parameters

        Mathematica: integrate[b*(x-a)^2, {x,1,0}]
        """
        dimension = 2
        a_list = [1, 2]
        b_list = [4, 5]
        f_list = [QuickConstruct(
            dimension=dimension,
            custom_fun=lambda x, a=a, b=b: b * (x - a) ** 2)
            for a, b in zip(a_list, b_list)]
        measure = Uniform(dimension=dimension)
        sol_data_list = [integrate(f, measure) for f in f_list]
        sols = [sol_data[0] for sol_data in sol_data_list]
        true_sols = [(b / 3) * (3 * a * (a - 1) + 1)
                     for a, b in zip(a_list, b_list)]
        abs_tol = sol_data_list[0][1].stopping_criterion.abs_tol
        max_error = max(abs(array(sols) - array(true_sols)))
        self.assertTrue(max_error < abs_tol)


if __name__ == "__main__":
    unittest.main()
