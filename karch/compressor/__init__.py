__all__ = ["Compressor", "Decompressor"]


class ThreeNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __hash__(self):
        return hash((self.left, self.right))

    def __str__(self):
        return "({}, {})".format(self.left, self.right)


def byte_to_bin(_byte):
    res = []
    while _byte > 0:
        res.append(_byte % 2 == 1)
        _byte //= 2
    while len(res) < 8:
        res.append(False)
    return res[::-1]


def div_up(value, module):
    if value % module > 0:
        return value // module + 1
    return value // module
