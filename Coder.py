def div_up(value, module):
    if value % module > 0:
        return value // module + 1
    return value // module


class Coder:
    def __init__(self):
        self._cnt = {}
        self._keys = {}
        self._adding_allow = True
        self._data = []
        self._splits_bits = [0]
        self._splits_bytes = [0]
        pass

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

    def _generate_dictionary(self):
        def subgenerator(code, item):
            if type(item) is int:
                self._keys[item] = list(code)
            else:
                subgenerator(list(code + [False]), item[0])
                subgenerator(list(code + [True]), item[1])

        self._adding_allow = False
        dict = set()
        for item in self._cnt.items():
            dict.add((item[1], item[0]))

        while len(dict) > 1:
            one = min(dict)
            dict.remove(one)
            two = min(dict)
            dict.remove(two)
            dict.add((one[0] + two[0], (one[1], two[1])))
        self._root = min(dict)[1]
        subgenerator([], self._root)

    def pack_sequence(self):
        def get_next_data(_pos_beg, _pos_end):
            for byte in self._data[_pos_beg: _pos_end]:
                yield self._keys[byte]

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
                for b in i:
                    if b:
                        current_byte += pos
                    pos //= 2
                    if pos == 0:
                        pos = 128
                        yield current_byte
                        cnt += 8
                        current_byte = 0
            if current_byte > 0:
                yield current_byte
                cnt += 8
                while pos > 0:
                    pos //= 2
                    cnt -= 1
            self._splits_bits.append(div_up(self._splits_bits[-1], 8) * 8 + cnt)

    def unpack_sequence(self, data, part_number):
        def get_next_byte(_start_with, bit_count):
            def byte_to_bin(_byte):
                res = []
                while _byte > 0:
                    res.append(_byte % 2 == 1)
                    _byte //= 2
                while len(res) < 8:
                    res.append(False)
                return res[::-1]

            cur = self._root
            for byte in data[_start_with:]:
                bins = byte_to_bin(byte)
                for i in bins:
                    if bit_count > 0:
                        bit_count -= 1
                        if not i:
                            cur = cur[0]
                        if i:
                            cur = cur[1]
                        if isinstance(cur, int):
                            yield cur
                            cur = self._root
                    else:
                        return

        start_with = div_up(self._splits_bits[part_number], 8)
        yield from get_next_byte(start_with,
                                 self._splits_bits[part_number + 1] - div_up(self._splits_bits[part_number], 8) * 8)

    def get_keys(self):
        return self._keys.copy()

    def get_points(self, generator):
        pass
