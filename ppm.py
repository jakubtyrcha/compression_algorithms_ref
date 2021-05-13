# this is a fast lookup / not-so-fast-but-amortized update cum count structure
# assumption: most contexts are sparse, for dense ones no linked list would be better (may do dense one for order 1-2 contexts and sparse one for order >2 or sth like that)
class CountArraySparse:
    def __init__(self, len):
        self.cum_counts = [0] * len
        self.prev = [-1] * len
        self.last = -1

    def contains(self, x):
        return x in self

    def __contains__(self, x):
        return self.cum_counts[x] > 0

    def increment_count(self, x):
        self.cum_counts[x] += 1

        if self.last == -1 or self.last == x:
            self.last = x
            return

        if self.last < x:
            self.prev[x] = self.last
            self.cum_counts[x] += self.cum_counts[self.last]
            self.last = x
            return

        j = self.last
        self.cum_counts[self.last] += 1

        i = self.prev[j]
        while i > x:
            self.cum_counts[i] += 1
            j = i
            i = self.prev[j]

        if i == x:
            return

        if i >= 0 and i < x and self.cum_counts[x] == 1: # new entry, accumulate prev
            self.cum_counts[x] += self.cum_counts[i]

        self.prev[j] = x
        self.prev[x] = i


    def get_count(self, x):
        if self.prev[x] == -1:
            return self.get_cum_count(x)
        return self.cum_counts[x] - self.cum_counts[self.prev[x]]

    def get_cum_count(self, x):
        return self.cum_counts[x]

    def get_total_count(self):
        if self.last == -1:
            return 0
        return self.cum_counts[self.last]

import math

def get_bit(value, index):
    return (value >> index) & 1

def msb(value, m):
    return get_bit(value, m - 1)

class ArithmeticEncoder:
    def __init__(self, m):
        self.m = m
        self.l = 0
        self.u = (1 << m) - 1
        self.scale3 = 0
        self.mask = (1 << m) - 1
        self.result = []

    def encode(self, range_l, range_u, range_max):
        l = self.l
        u = self.u
        scale3 = self.scale3
        m = self.m
        mask = self.mask

        l1 = self.l + math.floor((u - l + 1) * range_l / range_max)
        u1 = self.l + math.floor((u - l + 1) * range_u / range_max) - 1

        l = l1
        u = u1

        e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        while (msb(l, m) == msb(u, m)) or e3:
            if msb(l, m) == msb(u, m):
                b = msb(l, m)
                self.result.append(b)
                l = (l << 1) & mask
                u = ((u << 1) | 1) & mask

                while scale3 > 0:
                    self.result.append(b ^ 1)
                    scale3 = scale3 - 1
            if e3:
                l = l + (1 << (m - 2))
                l = (l << 1) & mask
                u = u + (1 << (m - 2))
                u = ((u << 1) | 1) & mask

                scale3 = scale3 + 1

            e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        self.l = l
        self.u = u
        self.scale3 = scale3

    def flush(self):
        l = self.l
        u = self.u
        scale3 = self.scale3
        m = self.m
        mask = self.mask

        self.result.append(msb(l, m))
        l = (l << 1) & mask
        tag_bits = 1

        while scale3 > 0:
            self.result.append(1)
            scale3 = scale3 - 1

        while tag_bits < m:
            self.result.append(msb(l, m))
            l = (l << 1) & mask
            tag_bits = tag_bits + 1

        return self.result

def encode(sequence, max_context_len, alphabet):
    contexts = dict()

    m = 30
    entropy_coder = ArithmeticEncoder(m)

    symbol_index = dict()
    cum_count = CountArraySparse(len(alphabet))
    for s in alphabet:
        index = len(symbol_index)
        symbol_index[s] = index
        cum_count.increment_count(index)

    contexts[None] = cum_count # -1 order
    contexts[''] = CountArraySparse(len(alphabet)) # 0 order

    i = 0
    while i < len(sequence):
        k = max(0, i - max_context_len)
        idx = symbol_index[sequence[i]]

        j = k
        encoded = False
        while j <= i:
            ctx_key = sequence[j:i]
            if ctx_key in contexts:
                # found context of some order
                ctx = contexts[ctx_key]
                if not encoded:
                    if idx in ctx:
                        # that context 'knows' the symbol
                        f_x_1 = ctx.get_cum_count(idx)
                        f_x = f_x_1 - ctx.get_count(idx)
                        entropy_coder.encode(f_x, f_x_1, ctx.get_total_count() + 1)
                        #print("encoded '{}' in context '{}'".format(sequence[i], ctx_key))
                        encoded = True
                        # todo: do we break here?
                    elif ctx.get_total_count() > 0:
                        # encode escape code
                        f_x = ctx.get_total_count()
                        f_x_1 = f_x + 1
                        #print("encoded %E in context '{}'".format(ctx_key))
                        entropy_coder.encode(f_x, f_x_1, f_x_1)

                ctx.increment_count(idx)
            else:
                assert encoded == False
                # context not found, create it and update counts
                contexts[ctx_key] = CountArraySparse(len(alphabet))
                contexts[ctx_key].increment_count(idx)

            j = j + 1

        if not encoded:
            # encode with -1 order
            ctx = contexts[None]
            f_x_1 = ctx.get_cum_count(idx)
            f_x = f_x_1 - ctx.get_count(idx)
            entropy_coder.encode(f_x, f_x_1, ctx.get_total_count())
            #print("encoded '{}' in context 'NONE'".format(sequence[i]))

        i = i + 1

    return entropy_coder.flush()

import functools

class ArithmeticDecoder:
    def __init__(self, m):
        self.m = m
        self.l = 0
        self.u = (1 << m) - 1
        self.scale3 = 0
        self.mask = (1 << m) - 1

    def start(self, sequence):
        self.t = functools.reduce(lambda x, y: (x << 1) | y, sequence[:self.m], 0)
        self.sequence_index = self.m

    def decode_symbol(self, ctx, has_escape):
        t = self.t
        l = self.l
        u = self.u

        range_max = ctx.get_total_count()
        if has_escape:
            range_max += 1
        symbol = 0
        C = math.floor(((t - l + 1) * range_max - 1) / (u - l + 1))
        while symbol < len(ctx.cum_counts) and (symbol not in ctx or C >= ctx.get_cum_count(symbol)): #todo: don't walk empty spaces
            symbol = symbol + 1

        range_l = 0
        range_u = 0

        if symbol < len(ctx.cum_counts):
            range_u = ctx.get_cum_count(symbol)
            range_l = ctx.get_cum_count(symbol) - ctx.get_count(symbol)
        else:
            assert has_escape
            range_l = ctx.get_total_count()
            range_u = range_l + 1

        l1 = l + math.floor((u - l + 1) * range_l / range_max)
        u1 = l + math.floor((u - l + 1) * range_u / range_max) - 1

        self.l = l1
        self.u = u1

        return symbol

    def decode_stream(self, prev_symbol, sequence, ctx):
        m = self.m
        mask = self.mask

        t = self.t
        l = self.l
        u = self.u
        sequence_index = self.sequence_index

        e3 = get_bit(l, m - 2) and not get_bit(u, m - 2)

        while (msb(l, m) == msb(u, m)) or e3:
            if msb(l, m) == msb(u, m):
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

        self.t = t
        self.l = l
        self.u = u
        self.sequence_index = sequence_index


def decode(sequence, max_context_len, alphabet, message_len):
    contexts = dict()

    m = 30
    entropy_coder = ArithmeticEncoder(m)

    symbol_index = dict()
    cum_count = CountArraySparse(len(alphabet))
    for s in alphabet:
        index = len(symbol_index)
        symbol_index[s] = index
        cum_count.increment_count(index)
    inv_symbol_index = {v: k for k, v in symbol_index.items()}

    contexts[None] = cum_count  # -1 order
    contexts[''] = CountArraySparse(len(alphabet))  # 0 order

    entropy_decoder = ArithmeticDecoder(m)
    entropy_decoder.start(sequence)

    symbol = entropy_decoder.decode_symbol(contexts[None], False)
    contexts[''].increment_count(symbol)
    msg = inv_symbol_index[symbol]
    #print("context '{}' adds idx {}".format('', symbol))
    #print("context '{}' adds symbol '{}'".format('', msg[-1]))

    i = 1
    while len(msg) < message_len:
        k = max(0, i - max_context_len)

        #
        j = k
        while j <= i:
            ctx_key = msg[j:i]
            if ctx_key in contexts:
                ctx = contexts[ctx_key]
                # decode symbol for the context!

                if ctx.get_total_count() > 0:
                    entropy_decoder.decode_stream(symbol, sequence, ctx)
                    popped_symbol = entropy_decoder.decode_symbol(ctx, True)

                    if popped_symbol < len(alphabet): # not escape
                        symbol = popped_symbol
                        msg += inv_symbol_index[symbol]
                        #print("decoded '{}' in context '{}'".format(msg[-1], ctx_key))
                        break
                    else:
                        #print("decoded %E in context '{}'".format(ctx_key))
                        pass

            j = j + 1

        if j == i + 1: # fallback to order -1
            ctx = contexts[None]
            entropy_decoder.decode_stream(symbol, sequence, ctx)
            symbol = entropy_decoder.decode_symbol(ctx, False)
            assert symbol < len(alphabet) # no escape for order -1
            msg += inv_symbol_index[symbol]
            #print("decoded '{}' in context 'NONE'".format(msg[-1]))

        j = k
        while j <= i:
            ctx_key = msg[j:i]
            if ctx_key not in contexts:
                contexts[ctx_key] = CountArraySparse(len(alphabet))
            ctx = contexts[ctx_key]

            #print("context '{}' adds idx {}".format(ctx_key, symbol))
            #print("context '{}' adds symbol '{}'".format(ctx_key, msg[-1]))
            ctx.increment_count(symbol)

            j = j + 1

        i = i + 1

    return msg

sequence = 'this is the tithe'

e = encode(sequence, 2, 'abcdefghijklmnopqrstuvwxyz ')
print(e)
print(decode(e, 2, 'abcdefghijklmnopqrstuvwxyz ', len(sequence)))

def decode(sequence, max_context_len, alphabet):
    pass

import unittest

class PpmTestCase(unittest.TestCase):
    def test_count_array_sparse(self):
        ca = CountArraySparse(3)
        ca.increment_count(0)

        self.assertEqual(ca.contains(0), True)
        self.assertEqual(ca.contains(1), False)
        self.assertEqual(ca.contains(2), False)
        self.assertEqual(ca.get_cum_count(0), 1)
        self.assertEqual(ca.get_count(0), 1)

        ca = CountArraySparse(3)
        ca.increment_count(1)

        self.assertEqual(ca.contains(0), False)
        self.assertEqual(ca.contains(1), True)
        self.assertEqual(ca.contains(2), False)
        self.assertEqual(ca.get_cum_count(1), 1)
        self.assertEqual(ca.get_count(1), 1)

        ca = CountArraySparse(10)
        ca.increment_count(1)
        ca.increment_count(1)
        ca.increment_count(1)

        ca.increment_count(2)

        ca.increment_count(4)
        ca.increment_count(4)

        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)

        for x in range(0, 10):
            if x in {1,2,4,9}:
                self.assertEqual(ca.contains(x), True)
            else:
                self.assertEqual(ca.contains(x), False)

        self.assertEqual(ca.get_count(1), 3)
        self.assertEqual(ca.get_cum_count(1), 3)
        self.assertEqual(ca.get_count(2), 1)
        self.assertEqual(ca.get_cum_count(2), 4)
        self.assertEqual(ca.get_count(4), 2)
        self.assertEqual(ca.get_cum_count(4), 6)
        self.assertEqual(ca.get_count(9), 5)
        self.assertEqual(ca.get_cum_count(9), 11)

        self.assertEqual(ca.get_total_count(), 11)

        ca = CountArraySparse(10)
        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)
        ca.increment_count(9)

        ca.increment_count(4)
        ca.increment_count(4)

        ca.increment_count(2)

        ca.increment_count(1)
        ca.increment_count(1)
        ca.increment_count(1)

        for x in range(0, 10):
            if x in {1,2,4,9}:
                self.assertEqual(ca.contains(x), True)
            else:
                self.assertEqual(ca.contains(x), False)

        self.assertEqual(ca.get_count(1), 3)
        self.assertEqual(ca.get_cum_count(1), 3)
        self.assertEqual(ca.get_count(2), 1)
        self.assertEqual(ca.get_cum_count(2), 4)
        self.assertEqual(ca.get_count(4), 2)
        self.assertEqual(ca.get_cum_count(4), 6)
        self.assertEqual(ca.get_count(9), 5)
        self.assertEqual(ca.get_cum_count(9), 11)

        self.assertEqual(ca.get_total_count(), 11)

        ca = CountArraySparse(28)
        ca.increment_count(19)
        ca.increment_count(7)
        ca.increment_count(8)

        self.assertEqual(ca.get_cum_count(7), 1)
        self.assertEqual(ca.get_cum_count(8), 2)
        self.assertEqual(ca.get_cum_count(19), 3)

        ca.increment_count(18)
        ca.increment_count(26)
        ca.increment_count(19)

        self.assertEqual(ca.get_cum_count(7), 1)
        self.assertEqual(ca.get_cum_count(8), 2)
        self.assertEqual(ca.get_cum_count(18), 3)
        self.assertEqual(ca.get_cum_count(19), 5)
        self.assertEqual(ca.get_cum_count(26), 6)


    def test_book(self):
        sequence = 'this is the tithe'

        #encode(sequence, 2, 'abcedefghijklmnopqrstuvwxyz ')
