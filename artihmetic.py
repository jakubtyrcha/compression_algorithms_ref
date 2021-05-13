import itertools
import functools
import math

def get_cum_count(counts):
    return [0] + list(itertools.accumulate(counts))

def get_min_word_len(counts):
    return (get_cum_count(counts)[-1] * 4).bit_length()

def encode(cum_count, m, sequence):
    result = []

    l = 0
    u = (1 << m) - 1
    total_count = cum_count[-1]
    scale3 = 0
    mask = (1 << m) - 1

    def get_bit(value, index):
        return (value >> index) & 1

    def msb(value):
        return get_bit(value, m - 1)

    for symbol in sequence:
        l1 = l + math.floor((u - l + 1) * cum_count[symbol] / total_count)
        u1 = l + math.floor((u - l + 1) * cum_count[symbol + 1] / total_count) - 1

        l = l1
        u = u1

        e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        while (msb(l) == msb(u)) or e3:
            if msb(l) == msb(u):
                b = msb(l)
                result.append(b)
                l = (l << 1) & mask
                u = ((u << 1) | 1) & mask

                while scale3 > 0:
                    result.append(b ^ 1)
                    scale3 = scale3 - 1
            if e3:
                l = l + (1 << (m - 2))
                l = (l << 1) & mask
                u = u + (1 << (m - 2))
                u = ((u << 1) | 1) & mask

                scale3 = scale3 + 1

            e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

    result.append(msb(l))
    l = (l << 1) & mask
    tag_bits = 1

    while scale3 > 0:
        result.append(1)
        scale3 = scale3 - 1

    while tag_bits < m:
        result.append(msb(l))
        l = (l << 1) & mask
        tag_bits = tag_bits + 1

    return result

def decode(cum_count, m, sequence, dec_len):
    result = []

    l = 0
    u = (1 << m) - 1
    total_count = cum_count[-1]
    scale3 = 0
    mask = (1 << m) - 1

    def get_bit(value, index):
        return (value >> index) & 1

    def msb(value):
        return get_bit(value, m - 1)

    t = functools.reduce(lambda x, y: (x << 1) | y, sequence[:m], 0)
    sequence_index = m

    def decode_symbol():
        symbol = 0
        C = math.floor(((t - l + 1) * total_count - 1) / (u - l + 1))
        while C >= cum_count[symbol + 1]:
            symbol = symbol + 1
        return symbol

    symbol = decode_symbol()
    result.append(symbol)

    while len(result) < dec_len:

        l1 = l + math.floor((u - l + 1) * cum_count[symbol] / total_count)
        u1 = l + math.floor((u - l + 1) * cum_count[symbol + 1] / total_count) - 1

        l = l1
        u = u1

        e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        while (msb(l) == msb(u)) or e3:
            if msb(l) == msb(u):
                l = (l << 1) & mask
                u = ((u << 1) | 1) & mask

                t = (t << 1) & mask
                t |= sequence[sequence_index]
                sequence_index = sequence_index + 1

                if sequence_index == len(sequence):
                    break

            if e3:
                l = l + (1 << (m - 2))
                l = (l << 1) & mask
                u = u + (1 << (m - 2))
                u = ((u << 1) | 1) & mask
                t = t + (1 << (m - 2))
                t = (t << 1) & mask
                t |= sequence[sequence_index]
                sequence_index = sequence_index + 1

                if sequence_index == len(sequence):
                    break

            e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        symbol = decode_symbol()
        result.append(symbol)

    return result

import unittest
import random

class ArithmeticTestCase(unittest.TestCase):
    def test_utils(self):
        self.assertEqual(get_min_word_len([40, 1, 9]), 8)

    def test_encode_decode_book(self):
        counts = [40, 1, 9]
        enc = encode(get_cum_count(counts), get_min_word_len(counts), [0, 2, 1, 0])
        self.assertEqual(enc, [1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])

        dec = decode(get_cum_count(counts), get_min_word_len(counts), enc, 4)
        self.assertEqual(dec, [0, 2, 1, 0])


    def _test_series(self, counts, series):
        C = get_cum_count(counts)
        m = get_min_word_len(counts)

        for s in series:
            enc = encode(C, m, s)
            dec = decode(C, m, enc, len(s))

            self.assertEqual(dec, s)

    def test_encode_decode(self):
        self._test_series([1, 2], [[0, 0], [1, 1], [0, 1], [1, 0]])
        self._test_series([40, 1, 9], [[0], [1], [0, 1], [1, 0], [0, 1, 1, 0]])
        self._test_series([41, 1, 9], [[0], [1], [0, 1], [1, 0], [0, 1, 1, 0]])

        sequences = []
        for i in range(1, 100):
            sequences.append([0] * i)
            sequences.append([1] * i)
        self._test_series([100000, 1], sequences)

    def test_random(self):
        random.seed(0)

        for i in range(1, 64):
            sequences = []

            for j in range(32):
                s = []
                X = random.getrandbits(32)
                for _ in range(16):
                    s.append(X & 3)
                    X = X >> 2
                sequences.append(s)

            self._test_series([i, 1, 2, 1], sequences)

    def test_distributions(self):
        random.seed(0)
        alphabet_size = 7
        counts = [1] * alphabet_size

        for _ in range(100):
            x = math.floor(random.betavariate(5, 1) * alphabet_size)
            counts[x] += 1

            sequences = []

        for n in range(10, 100, 10):
            s = []
            for _ in range(n):
                x = math.floor(random.betavariate(5, 1) * alphabet_size)
                s.append(x)
                sequences.append(s)

        self._test_series(counts, sequences)

    def test_big(self):
        random.seed(0)
        alphabet_size = 10
        counts = [1] * alphabet_size
        s = []

        for _ in range(1000000):
            x = math.floor(random.betavariate(5, 1) * alphabet_size)
            counts[x] += 1
            s.append(x)

        self._test_series(counts, [s])
