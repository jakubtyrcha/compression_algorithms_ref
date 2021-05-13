from bisect import bisect_right

def build_huffman_code(frequency):
    frequency = sorted(frequency, key = lambda x: x[1])
    sorted_freq = [freq for (s, freq) in frequency]
    sorted_nodes = [[s, None, None ] for (s, freq) in frequency]

    while(len(sorted_freq) > 1):
        freq0, l = (sorted_freq.pop(0), sorted_nodes.pop(0))
        freq1, r = (sorted_freq.pop(0), sorted_nodes.pop(0))

        node = (freq0 + freq1, [None, l, r])
        i = bisect_right(sorted_freq, node[0])

        sorted_freq.insert(i, node[0])
        sorted_nodes.insert(i, node[1])

    lookup = [None] * 256
    def walk_tree(node, acc, lookup):
        (s, l, r) = node
        if s != None:
            lookup[s] = acc
        if l:
            walk_tree(l, acc + '0', lookup)
        if r:
            walk_tree(r, acc + '1', lookup)

    root = sorted_nodes[0]
    walk_tree(root, '', lookup)

    return (root, lookup)

def encode(code, sequence):
    result = ''

    for s in sequence:
        b = code[1][s]
        result += b

    return result

def decode(code, sequence):
    result = []
    i = 0

    while i < len(sequence):
        node = code[0]

        while node:

            if node[0] != None:
                result.append(node[0])
                break

            b = sequence[i]
            i = i + 1
            if b == '0':
                node = node[1]
            else:
                node = node[2]

    return result

import unittest
import random
from utils import get_average_codelength, build_frequency

class HuffmanTestCase(unittest.TestCase):
    def test_building_huffman(self):
        freq = [(0, 4), (1, 2), (2, 2), (3, 1), (4, 1)]
        code = build_huffman_code(freq)
        self.assertAlmostEqual(get_average_codelength(code, freq), 2.2, 1)

        freq = [(0, 1), (1, 1)]
        code = build_huffman_code(freq)
        self.assertAlmostEqual(get_average_codelength(code, freq), 1, 0)

        freq = [(0, 80), (1, 2), (2, 18)]
        code = build_huffman_code(freq)
        self.assertAlmostEqual(get_average_codelength(code, freq), 1.2, 1)

        freq = [(0, 95), (1, 2), (2, 3)]
        code = build_huffman_code(freq)
        self.assertAlmostEqual(get_average_codelength(code, freq), 1.05, 2)

    def test_encode_decode(self):
        freq = [(0, 10), (1, 2), (2, 2), (3, 1), (4, 1)]
        sequence = [0, 0, 0, 0, 1, 2]
        code = build_huffman_code(freq)
        self.assertEqual(sequence, decode(code, encode(code, sequence)))

    def test_encode_decode_randomized(self):
        alphabet_size = 50
        random.seed(0)

        sequence = []
        for _ in range(1000):
            sequence.append(int(random.betavariate(1, 5) * alphabet_size))

        f = build_frequency(sequence)
        code = build_huffman_code(f)

        self.assertEqual(sequence, decode(code, encode(code, sequence)))