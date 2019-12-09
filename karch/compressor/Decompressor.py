from karch.compressor.__init__ import ThreeNode
from karch.compressor.__init__ import byte_to_bin
from karch.compressor.__init__ import div_up


class Decompressor:
    def __init__(self):
        self._keys = {}
        self._splits_bits = [0]
        self._root = ThreeNode(-1, -1)

    def _get_next_byte(self, data, _start_with, bit_count, work):
        cur = self._root
        for ix in range(_start_with, len(data)):
            work.do_progress(work.progress + 1)
            byte = data[ix]
            bins = byte_to_bin(byte)
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

    def unpack_sequence(self, data, part_number, work):
        if self._root is None:
            raise Exception("The keys are not detected")
        start_with = div_up(self._splits_bits[part_number], 8)
        if part_number == len(self._splits_bits) - 1:
            work.volume = len(data) - start_with
        else:
            work.volume = div_up(self._splits_bits[part_number + 1] - self._splits_bits[part_number], 8)
        work.progress = 0
        yield from self._get_next_byte(
            data,
            start_with,
            self._splits_bits[part_number + 1] - div_up(self._splits_bits[part_number], 8) * 8,
            work
        )
        work.finish()

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
            bins = byte_to_bin(next(it))
            count_for_return += 1
            for i in range(len(bins)):
                if bins[i]:
                    three.append(way(i + index))
            index += len(bins)

        self._root = ThreeNode(-1, -1)

        for i in range(count):
            cur = self._root
            key = next(it)
            for j in three[i][:-1]:
                if not j:
                    if isinstance(cur.left, int):
                        cur.left = ThreeNode(-1, -1)
                    cur = cur.left
                if j:
                    if isinstance(cur.right, int):
                        cur.right = ThreeNode(-1, -1)
                    cur = cur.right
            if not three[i][-1]:
                cur.left = key
            else:
                cur.right = key

        return count_for_return

    def set_sizes_of_parts(self, list_sizes_of_parts):
        self._splits_bits = [0] + list_sizes_of_parts
