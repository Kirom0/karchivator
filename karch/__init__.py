import os
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
    sys_dev_null = ""
    if sys.platform == "win32":
        sys_dev_null = ">2 NUL"
    if sys_dev_null == "linux2":
        sys_dev_null = "2> /dev/null"
    os.system("mkdir {} ".format(dirname) + sys_dev_null)
