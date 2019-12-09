import os
from karch.compressor import *
from pathlib import Path
from karch.__init__ import bins_to_int
from karch.__init__ import make_dir
from console_progress import *


def decoder(archive_name):
    def generator_of_list_part(mas, start_with, end_on):
        for i in range(start_with, end_on):
            yield mas[i]

    if not os.path.exists(archive_name):
        raise Exception("Ошибка. Файла \"{}\" не существует.".format(archive_name))
    try:
        arch = open(archive_name, "rb")
    except PermissionError:
        raise Exception("Ошибка. Файл \"{}\" занят другим процессом".format(archive_name))

    assert arch.read(5) == b'karch'
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
        work = Work.Work("Unpacking files {}/{}".format(i + 1, count_of_files), 1)
        archive_name = bytearray(decompressor.unpack_sequence(data, i, work))
        _file = (archive / (archive_name[:names[i]]).decode('utf-8'))
        make_dir(_file)
        _file.write_bytes(archive_name[names[i]:])

    del decompressor
