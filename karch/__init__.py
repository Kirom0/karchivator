import os
from pathlib import Path
import sys

__all__ = ["Coder", "Decoder"]


def bins_to_int(value):
    res = 0
    category = 1
    for i in range(len(value) - 1, -1, -1):
        res += value[i] * category
        category *= 256
    return res


def int_to_bins(value, size):
    res = []
    t = value
    for i in range(size):
        res.append(t % 256)
        t //= 256
    return res[::-1]


def make_dir(dirname):
    for i in list(dirname.parents)[::-1][1:]:
        try:
            i.mkdir()
        except FileExistsError:
            pass

def cut_common_dir(pure_path, depth):
    parents = list(pure_path.parts)[depth:]
    result = Path('.')
    for i in parents:
        result = result.joinpath(i)

    return str(result)
