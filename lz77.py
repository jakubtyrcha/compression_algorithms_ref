def encode(sequence, S):
    result = []
    N = len(sequence)

    if N == 0:
        return result

    result.append((0, 0, sequence[0]))

    i = 1
    while i < N:
        j = max(0, i - S)
        best_match_len = 0
        best_match_start = 0
        while j < i:
            match_len = 0
            match_start = j
            while i + match_len + 1 < N and sequence[match_start + match_len] == sequence[i + match_len]:
                match_len = match_len + 1
            if match_len > best_match_len:
                best_match_len = match_len
                best_match_start = match_start
            j = j + 1
        if best_match_len == 0:
            result.append((0, 0, sequence[i]))
            i = i + 1
            continue

        result.append((i - best_match_start, best_match_len, sequence[i + best_match_len]))
        i = i + best_match_len + 1

    return result

def decode(opcodes):
    result = []

    for (o, l, c) in opcodes:
        if o == 0:
            assert l == 0
            result.append(c)
            continue

        i = len(result) - o
        for _ in range(l):
            result.append(result[i])
            i = i + 1
        result.append(c)

    return ''.join(result)

import unittest
import random

class Lz77TestCase(unittest.TestCase):
    def test_book(self):
        t = 'cabracadabrar'
        self.assertEqual(t, decode(encode(t, 6)))

        t = 'abcdefghi' * 3
        self.assertEqual(t, decode(encode(t, 8)))
        self.assertEqual(len(encode(t, 8)), len(t))
        self.assertEqual(t, decode(encode(t, 9)))
        self.assertLess(len(encode(t, 9)), len(t))

    def test_artificial(self):
        t = 'a'
        t1 = 'a'

        for _ in range(100):
            t += 'a'
            t1 += ['a', 'b'][t1[-1] == 'a']
            self.assertEqual(t, decode(encode(t, 1)))
            self.assertEqual(t, decode(encode(t, 4)))
            self.assertEqual(t, decode(encode(t, 15)))
            self.assertEqual(t1, decode(encode(t1, 1)))
            self.assertEqual(t1, decode(encode(t1, 4)))
            self.assertEqual(t1, decode(encode(t1, 15)))

    def test_random(self):
        alphabet_size = 26
        random.seed(0)

        sequence = []
        for _ in range(1000):
            sequence.append(chr(ord('a') + int(random.betavariate(1, 5) * alphabet_size)))
        sequence = ''.join(sequence)

        self.assertEqual(sequence, decode(encode(sequence, 16)))

    def test_text(self):
        sequence = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo'
        self.assertEqual(sequence, decode(encode(sequence, 1000)))


