def div_up(value, module):
    if value % module > 0:
        return value // module + 1
    return value // module


class Compressor:
    def __init__(self):
        self._keys = {}
        self._splits_bits = [0]
        self._splits_bytes = [0]
        pass

    @staticmethod
    def byte_to_bin(_byte):
        res = []
        while _byte > 0:
            res.append(_byte % 2 == 1)
            _byte //= 2
        while len(res) < 8:
            res.append(False)
        return res[::-1]

    class ThreeNode:
        def __init__(self, left, right):
            self.left = left
            self.right = right

        def __hash__(self):
            return hash((self.left, self.right))

        def __str__(self):
            return "({}, {})".format(self.left, self.right)

    class Coder:
        def __init__(self):
            self.coder = Compressor()
            self._cnt = {}
            self._data = []
            self._adding_allow = True
            self._keys = self.coder._keys
            self._splits_bits = self.coder._splits_bits
            self._splits_bytes = self.coder._splits_bytes
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

        def _generate_dictionary(self):
            def subgenerator(code, _item):
                if type(_item) is int:
                    self._keys[_item] = list(code)
                    self._encoded_data_size += self._cnt[_item] * len(list(code))
                else:
                    subgenerator(list(code + [False]), _item.left)
                    subgenerator(list(code + [True]), _item.right)

            if len(self._cnt) == 1:
                raise Exception("Compressor.Compressor have got only one byte. Minimum 2 difference byte needed.")
            self._adding_allow = False
            dict = set()
            for item in self._cnt.items():
                dict.add((item[1], item[0]))

            while len(dict) > 1:
                one = (1000000000000000000, 0)
                for i in dict:
                    if i[0] < one[0]:
                        one = i
                dict.remove(one)
                two = (1000000000000000000, 0)
                for i in dict:
                    if i[0] < two[0]:
                        two = i
                dict.remove(two)
                dict.add((one[0] + two[0], Compressor.ThreeNode(one[1], two[1])))
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
                if pos < 128:
                    yield current_byte
                    cnt += 8
                    while pos > 0:
                        pos //= 2
                        cnt -= 1
                self._splits_bits.append(div_up(self._splits_bits[-1], 8) * 8 + cnt)

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


    class Decoder:
        def __init__(self):
            self.coder = Compressor()
            self._keys = self.coder._keys
            self._splits_bits = self.coder._splits_bits
            self._root = Compressor.ThreeNode(-1, -1)

        def unpack_sequence(self, data, part_number):
            def get_next_byte(_start_with, bit_count):
                cur = self._root
                for byte in data[_start_with:]:
                    bins = Compressor.byte_to_bin(byte)
                    for i in bins:
                        if bit_count > 0:
                            bit_count -= 1
                            if not i:
                                cur = cur.left
                            if i:
                                cur = cur.right
                            if isinstance(cur, int):
                                yield cur
                                cur = self._root
                        else:
                            return

            if self._root is None:
                raise Exception("The keys are not detected")
            start_with = div_up(self._splits_bits[part_number], 8)
            yield from get_next_byte(start_with,
                                     self._splits_bits[part_number + 1] - div_up(self._splits_bits[part_number], 8) * 8)

        def decode_keys(self, generator_data):
            def way(a):
                res = []
                while a > 1:
                    res.append(a % 2 == 1)
                    a //= 2
                return res[::-1]

            it = iter(generator_data)
            count = next(it) + 1
            count_for_return = count + 1
            three = []
            index = 2
            while len(three) < count:
                bins = Compressor.byte_to_bin(next(it))
                count_for_return += 1
                for i in range(len(bins)):
                    if bins[i]:
                        three.append(way(i + index))
                index += len(bins)

            self._root = Compressor.ThreeNode(-1, -1)

            for i in range(count):
                cur = self._root
                key = next(it)
                for j in three[i][:-1]:
                    if not j:
                        if isinstance(cur.left, int):
                            cur.left = Compressor.ThreeNode(-1, -1)
                        cur = cur.left
                    if j:
                        if isinstance(cur.right, int):
                            cur.right = Compressor.ThreeNode(-1, -1)
                        cur = cur.right
                if not three[i][-1]:
                    cur.left = key
                else:
                    cur.right = key

            return count_for_return

        def set_sizes_of_parts(self, list_sizes_of_parts):
            self._splits_bits = [0] + list_sizes_of_parts
