import os
from karch.compressor import *
from pathlib import Path
from karch.__init__ import bins_to_int
from karch.__init__ import make_dir
from karch.__init__ import calculate_file_hash
from console_progress import *


def decoder(archive_name):
    """
    :param archive_name: путь до архива
    :return: Распакованный archive_name в папке с таким же названием
    """
    def generator_of_list_part(mas, start_with, end_on):
        for i in range(start_with, end_on):
            yield mas[i]

    archive_size = os.path.getsize(archive_name)
    if not os.path.exists(archive_name):
        raise Exception("Ошибка. Файла \"{}\" не существует.".format(archive_name))
    try:
        _hash_fact = calculate_file_hash(archive_name, archive_size - 4)
        arch = open(archive_name, "rb")
    except PermissionError:
        raise Exception("Ошибка. Файл \"{}\" занят другим процессом".format(archive_name))

    arch.seek(archive_size - 4)
    _hash_expected = bins_to_int(arch.read())

    arch.seek(0)

    if arch.read(5) != b'karch' or _hash_fact != _hash_expected:
        raise Exception("Ошибка. Файл поврежден.")

    decompressor = Decompressor.Decompressor()
    print("Reading...")

    data = arch.read()

    count = decompressor.decode_keys(data)

    arch.seek(count + 5)
    count_of_files = bins_to_int(bytearray(arch.read(2)))
    parts = []
    names = []
    for i in range(count_of_files):
        parts.append(bins_to_int(bytearray(arch.read(4))))
        names.append(bins_to_int(bytearray(arch.read(1))))

    decompressor.set_sizes_of_parts(parts)
    data = data[count + 2 + 5 * count_of_files:]

    archive = Path(os.path.splitext(archive_name)[0])
    for i in range(count_of_files):
        work = ProgressBar.ProgressBar("Unpacking files {}/{}".format(i + 1, count_of_files), 1)
        archive_name = bytearray(decompressor.unpack_sequence(data, i, work))
        _file = (archive / (archive_name[:names[i]]).decode('utf-8'))
        make_dir(_file)
        _file.write_bytes(archive_name[names[i]:])

    del decompressor
