import unittest
import random
import os
from karch.compressor import *
from console_progress import *


class Test_compressor_and_decompressor(unittest.TestCase):
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

    def test_two_key(self):
        data = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\1'

        compressor = Compressor.Compressor()
        compressor.append_data(data)
        packed_data = bytes(compressor.pack_sequence())

        decompressor = Decompressor.Decompressor()
        decompressor.decode_keys((compressor.encode_keys()))
        decompressor.set_sizes_of_parts(compressor.get_sizes_of_parts())

        self.assertEqual(data,
                         bytes(decompressor.unpack_sequence(packed_data, 0, ProgressBar.ProgressBar('Unpacking', 1))))

    def test_one_random_sequence(self):
        data = bytearray()
        for i in range(1000):
            data += bytes([random.randint(0, 255)])

        compressor = Compressor.Compressor()
        compressor.append_data(data)
        packed_data = bytes(compressor.pack_sequence())

        decompressor = Decompressor.Decompressor()
        decompressor.decode_keys((compressor.encode_keys()))
        decompressor.set_sizes_of_parts(compressor.get_sizes_of_parts())

        self.assertEqual(data, bytes(decompressor.unpack_sequence(packed_data, 0, ProgressBar.ProgressBar('Unpacking', 1))))

    def test_complicated(self):
        def to_bin(a):
            if a:
                return '1'
            return '0'

        def file_data_gen(path):
            yield from bytearray(os.path.basename(path), encoding='ascii')
            yield from b'aaabbabbabbaabbbabbbccc'

        compressor = Compressor.Compressor()
        data = list()
        data.append(b'abaacabaaa')
        #data.append(file_data_gen('one.txt'))
        data.append(b'asdahsdjhqiuwdqwjdoqwnduqbwudqnwoinqwubdyqwiodqwmduqibwdqowmdqwbdqwndiqmwdbqwyhdoqwimsuqwsyqjwsq')
        for i in data:
            compressor.append_data(i)
        ls = list()
        for i in compressor.pack_sequence():
            ls.append(i)

        decompressor = Decompressor.Decompressor()
        decompressor.decode_keys(compressor.encode_keys())
        decompressor.set_sizes_of_parts(compressor.get_sizes_of_parts())

        ans = list()

        for j in range(len(data)):
            ans.append(list())
            for i in decompressor.unpack_sequence(ls, j, ProgressBar.ProgressBar("Unpacking {}/{}".format(j + 1, len(data)), 1)):
                ans[j].append(i)
            self.assertEqual(list(bytearray(data[j])), ans[j])

