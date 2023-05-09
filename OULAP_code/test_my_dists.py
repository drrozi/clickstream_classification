import unittest
import my_dists
import numpy as np

class TestTraFre(unittest.TestCase):

    def test_zigzag1d(self):
        a = np.array([0.0, 1.0, 1.0, 1.0])
        b = np.array([1.0, 0.0, 1.0, 0.0])
        self.assertEqual(round(my_dists.trafre(a,b), 3), 1)

class TestDiscFrechet(unittest.TestCase):

    def test_zigzag1d(self):
        a = np.array([0.0, 1.0, 1.0, 1.0])
        b = np.array([1.0, 0.0, 1.0, 0.0])
        c = np.array([0.0, 1.0])
        self.assertEqual(round(my_dists.disc_frechet(a,b), 3), 1)
        self.assertEqual(round(my_dists.disc_frechet(a,c), 3), 0)

class TestDiscDTW(unittest.TestCase):

    def test_zigzag1d(self):
        a = np.array([0.0, 1.0, 1.0, 1.0])
        b = np.array([1.0, 0.0, 1.0, 0.0])
        c = np.array([0.0, 1.0])
        self.assertEqual(round(my_dists.disc_dtw(a,b), 3), 2)
        self.assertEqual(round(my_dists.disc_dtw(a,c), 3), 0)


if __name__ == '__main__':
    unittest.main()

