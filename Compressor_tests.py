import unittest
import os
from Compressor import Compressor


class Compressor_tests(unittest.TestCase):

    @staticmethod
    def data_adding(coder):
        s = b'abaacabaaa'
        coder.append_data(s)

    @staticmethod
    def byte_to_bin(byte):
        res = []
        while byte > 0:
            res.append(byte % 2 == 1)
            byte //= 2
        while len(res) < 8:
            res.append(False)
        return res[::-1]

    def test_test(self):
        def to_bin(a):
            if a:
                return '1'
            return '0'

        def file_data_gen(path):
            yield from bytearray(os.path.basename(path), encoding='ascii')
            yield from b'aaabbabbabbaabbbabbbccc'

        coder = Compressor.Coder()
        data = list()
        data.append(b'abaacabaaa')
        #data.append(file_data_gen('one.txt'))
        data.append(b'asdahsdjhqiuwdqwjdoqwnduqbwudqnwoinqwubdyqwiodqwmduqibwdqowmdqwbdqwndiqmwdbqwyhdoqwimsuqwsyqjwsq')
        for i in data:
            coder.append_data(i)
        ls = list()
        for i in coder.pack_sequence():
            ls.append(i)

        decoder = Compressor.Decoder()
        decoder.decode_keys(coder.encode_keys())
        decoder.set_sizes_of_parts(coder.get_sizes_of_parts())

        ans = list()
        for j in range(len(data)):
            ans.append(list())
            for i in decoder.unpack_sequence(ls, j):
                ans[j].append(i)
            self.assertEqual(list(bytearray(data[j])), ans[j])

