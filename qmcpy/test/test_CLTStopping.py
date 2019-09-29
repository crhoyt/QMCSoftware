import unittest

from algorithms.stop import DistributionCompatibilityError
from algorithms.stop.CLTStopping import CLTStopping
from algorithms.distribution.QuasiRandom import QuasiRandom
from algorithms.distribution import measure

class Test_CLTStopping(unittest.TestCase):

    def test_Incompatible_Distrib(self):
        self.assertRaises(DistributionCompatibilityError,CLTStopping,QuasiRandom(measure().lattice()))

if __name__ == "__main__":
    unittest.main()