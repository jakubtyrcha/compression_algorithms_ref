def encode(sequence):
    d = dict()
    result = []

    i = 0

    while i < len(sequence):
        if i + 1 == len(sequence):
            result.append((0, sequence[i]))
            break

        if sequence[i] not in d:
            result.append((0, sequence[i]))
            d[sequence[i]] = len(d) + 1
            i = i + 1
            continue

        j = i + 1
        while j + 1 < len(sequence) and sequence[i:j + 1] in d:
            j = j + 1

        result.append((d[sequence[i:j]], sequence[j]))

        if j + 1 < len(sequence) and sequence[i:j + 1] not in d:
            d[sequence[i:j+1]] = len(d) + 1

        i = j + 1

    return result

def decode(e):
    d = dict()
    result = []

    for (index, symbol) in e:
        if index == 0:
            result.append(symbol)
            d[len(d) + 1] = [symbol]
            continue

        result += d[index] + [symbol]
        d[len(d) + 1] = d[index] + [symbol]

    return ''.join(result)

import unittest

class Lz78TestCase(unittest.TestCase):
    def test_book(self):
        s = 'wabba wabba wabba wabba woo woo woo'
        self.assertEqual(s, decode(encode(s)))

    def test_simple(self):
        for i in range(2048):
            s = ''
            while i > 0:
                s += ['b', 'a'][i & 1]
                i = i >> 1
            self.assertEqual(s, decode(encode(s)))

