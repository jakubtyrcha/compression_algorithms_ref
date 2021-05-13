import functools
import math

def get_average_codelength(code, freq):
    sum = functools.reduce(lambda x, y : x + y, [a[1] for a in freq])
    return functools.reduce(lambda x, y: x + len(code[1][y[0]]) * y[1] / sum, freq, 0)

def get_entropy(freq):
    sum = functools.reduce(lambda x, y: x + y, [a[1] for a in freq])
    return -functools.reduce(lambda x, y: x + y[1] / sum * math.log2(y[1] / sum), [x for x in freq if x[1] > 0], 0)

def build_frequency(sequence):
    counts = dict()
    for i in sequence:
        counts[i] = counts.get(i, 0) + 1
    return list(counts.items())

import unittest

class UtilsTestCase(unittest.TestCase):
    def test_entropy(self):
        self.assertEqual(get_entropy([(0, 1)]), 0)
        self.assertEqual(get_entropy([(0, 1), (1, 1)]), 1)
        self.assertAlmostEqual(get_entropy([(0, 4), (1, 2), (2, 2), (3, 1), (4, 1)]), 2.12, 2)
        self.assertAlmostEqual(get_entropy([(0, 80), (1, 2), (2, 18)]), 0.816, 3)
        self.assertAlmostEqual(get_entropy([(0, 95), (1, 2), (2, 3)]), 0.335, 3)

    def test_frequency(self):
        self.assertEqual(build_frequency([0, 1]), [(0, 1), (1, 1)])
        self.assertEqual(build_frequency([0, 1, 1, 1, 0]), [(0, 2), (1, 3)])
        self.assertEqual(build_frequency([0, 1, 2, 2, 2, 2]), [(0, 1), (1, 1), (2, 4)])