from karch.compressor.__init__ import ThreeNode
from karch.compressor.__init__ import div_up
from console_progress import *


class Compressor:
    def __init__(self):
        self._cnt = {}
        self._data = []
        self._adding_allow = True
        self._keys = {}
        self._splits_bits = [0]
        self._splits_bytes = [0]
        self._encoded_data_size = 0

    def append_data(self, generator):
        if not self._adding_allow:
            raise Exception("append_data are no allow already.")
        cnt = 0
        for byte in generator:
            cnt += 1
            self._data.append(byte)
            if byte in self._cnt:
                self._cnt[byte] += 1
            else:
                self._cnt[byte] = 1
        self._splits_bytes.append(cnt + self._splits_bytes[-1])

    def _sub_generate_dictionary(self, code, _item):
        if type(_item) is int:
            self._keys[_item] = list(code)
            self._encoded_data_size += self._cnt[_item] * len(list(code))
        else:
            self._sub_generate_dictionary(list(code + [False]), _item.left)
            self._sub_generate_dictionary(list(code + [True]), _item.right)

    def _generate_dictionary(self):
        if len(self._cnt) == 1:
            raise Exception("compressor.compressor have got only one byte. Minimum 2 difference byte needed.")
        self._adding_allow = False
        three = set()
        for item in self._cnt.items():
            three.add((item[1], item[0]))

        while len(three) > 1:
            one = (1000000000000000000, 0)
            for i in three:
                if i[0] < one[0]:
                    one = i
            three.remove(one)
            two = (1000000000000000000, 0)
            for i in three:
                if i[0] < two[0]:
                    two = i
            three.remove(two)
            three.add((one[0] + two[0], ThreeNode(one[1], two[1])))
        self._root = min(three)[1]
        self._sub_generate_dictionary([], self._root)

    def pack_sequence(self):
        def get_next_data(_pos_beg, _pos_end):
            for byte in self._data[_pos_beg: _pos_end]:
                yield self._keys[byte]

        bytes_count = sum(self._splits_bytes)
        work = Work.Work("Packing", bytes_count)
        if self._adding_allow:
            self._generate_dictionary()
        for part_number in range(len(self._splits_bytes) - 1):
            if not (0 <= part_number < len(self._splits_bytes)):
                raise ValueError("part_number is not in allowed range.")

            pos_beg = self._splits_bytes[part_number]
            if part_number + 1 >= len(self._splits_bytes):
                pos_end = div_up(len(self._data), 8)
                pos_end += 1
            else:
                pos_end = self._splits_bytes[part_number + 1]
            cnt = 0
            pos = 128
            current_byte = 0
            for i in get_next_data(pos_beg, pos_end):
                work.do_progress(work.progress + 1)
                for b in i:
                    if b:
                        current_byte += pos
                    pos //= 2
                    if pos == 0:
                        pos = 128
                        yield current_byte
                        cnt += 8
                        current_byte = 0
            if pos < 128:
                yield current_byte
                cnt += 8
                while pos > 0:
                    pos //= 2
                    cnt -= 1
            self._splits_bits.append(div_up(self._splits_bits[-1], 8) * 8 + cnt)
        work.finish()

    def encode_keys(self):
        def fill_three(_three, n, cur):
            if isinstance(cur, int):
                while len(_three) <= n - 2:
                    _three.append(-1)
                _three[n - 2] = cur
                return
            fill_three(_three, n * 2, cur.left)
            fill_three(_three, n * 2 + 1, cur.right)

        if self._adding_allow:
            self._generate_dictionary()
        three = [-1]
        fill_three(three, 1, self._root)
        result = []
        keys = []
        pos = 128
        current_byte = 0
        for i in range(len(three)):
            if three[i] >= 0:
                current_byte += pos
                keys.append(three[i])
            pos //= 2
            if pos == 0:
                pos = 128
                result.append(current_byte)
                current_byte = 0
        if current_byte > 0:
            result.append(current_byte)
        result = [len(self._cnt) - 1] + result + keys
        return result

    def get_keys_count(self):
        return len(self._keys)

    def get_root(self):
        return self._root

    def get_sizes_of_parts(self):
        return self._splits_bits[1:]

    def get_encoded_data_size(self):
        return self._encoded_data_size



