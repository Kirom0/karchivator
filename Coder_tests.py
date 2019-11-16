import unittest
from Coder import Coder


class Coder_tests(unittest.TestCase):

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

        coder = Coder()
        data = list()
        data.append(b'abaacabaaa')
        data.append(b'bbac')
        data.append(b'asdahsdjhqiuwdqwjdoqwnduqbwudqnwoinqwubdyqwiodqwmduqibwdqowmdqwbdqwndiqmwdbqwyhdoqwimsuqwsyqjwsq')
        coder.append_data(data[0])
        coder.append_data(data[1])
        ls = list()
        for i in coder.pack_sequence():
            ls.append(i)
        print(ls)
        rt = []
        for i in ls:
            print(*list(map(to_bin, Coder_tests.byte_to_bin(i))), end='', sep='')
        print()
        ans = list()
        for j in range(2):
            ans.append(list())
            for i in coder.unpack_sequence(ls, j):
                ans[j].append(i)
            self.assertEqual(list(bytearray(data[j])), ans[j])
