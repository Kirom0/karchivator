import os
from karch.compressor import *
from karch.__init__ import bins_to_int


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

    os.system("mkdir {}".format(os.path.splitext(archive_name)[0]))
    _dir = bytearray(os.path.splitext(archive_name)[0] + '/', encoding="utf-8")
    for i in range(count_of_files):
        print("Unpacking file #{}".format(i))
        archive_name = bytearray(decompressor.unpack_sequence(data, i))
        print("Writing file #{}".format(i))
        with open((_dir + archive_name[:names[i]]).decode('utf-8'), 'wb') as f:
            f.write(archive_name[names[i]:])

    del decompressor
