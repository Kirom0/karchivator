import os
from pathlib import Path
import sys

__all__ = ["Coder", "Decoder"]


def bins_to_int(value):
    """
    :param value: последовательность байт
    :return: числовое значение, закодированное в value. (Младший бит - последний бит value)
    """
    res = 0
    category = 1
    for i in range(len(value) - 1, -1, -1):
        res += value[i] * category
        category *= 256
    return res


def int_to_bins(value, size):
    """
    :param value: Числовое значение
    :param size: Размер возвращаемого листа
    :return: лист с закодированным в нём значением value, размера size. (Младший бит - последний бит value)
    """
    res = []
    t = value
    for i in range(size):
        res.append(t % 256)
        t //= 256
    return res[::-1]


def make_dir(filename):
    """
    :param filename: путь до файла, который в последствии будет создан
    :return: создание всех необходимых директорий для создания файла filename
    """
    for i in list(filename.parents)[::-1][1:]:
        try:
            i.mkdir()
        except FileExistsError:
            pass

def cut_common_dir(pure_path, depth):
    """
    :param pure_path: абсолютный pure_path к необходимому файлу
    :param depth: количество отсекаемых дирректорий
    :return: pure_path с отсеченным depth дирректорий с начала
    """
    parents = list(pure_path.parts)[depth:]
    result = Path('.')
    for i in parents:
        result = result.joinpath(i)

    return str(result)


def calculate_file_hash(path, count):
    """
    :param path: Путь до файла
    :param count: Количество байт
    :return: хеш count считанных байт из файла path
    """
    with open(path, "rb") as f:
        data = f.read(count)
    _hash = 1
    for i in data:
        pos = i
        while pos > 0:
            _hash *= 2
            if pos % 2 == 1:
                _hash += 1
            _hash %= 2147483647
            pos //= 2
    return _hash