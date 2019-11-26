import os
from karch.compressor import *
from karch.__init__ import int_to_bins


def coder(asker, result_filename, *filenames):
    def file_data_gen(path, file):
        yield from bytearray(os.path.basename(path), encoding='utf-8')
        yield from file.read()

    files = []
    if os.path.exists(result_filename):
        if not asker("Файл \"{}\" уже сущесвует. Перезаписать?".format(result_filename)):
            raise Exception("Ошибка. Отказ в записи.")
    for i in filenames:
        if not os.path.exists(i):
            raise Exception("Ошибка. Файл \"{}\" не найден.".format(i))

    for i in filenames:
        try:
            files.append(open(i, "rb"))
        except PermissionError:
            raise Exception("Ошибка. Файл \"{}\" занят другим процессом.".format(i))
    result = open(result_filename, "wb")

    # 5 байт - "karch"
    result.write(b"karch")

    compressor = Compressor.Compressor()
    for i in range(len(filenames)):
        compressor.append_data(file_data_gen(filenames[i], files[i]))

    # Запись таблицы для декодирования
    encoded_keys = compressor.encode_keys()
    try:
        result.write(bytearray(encoded_keys))
    except:
        raise Exception("Ошибка. Ошибка при кодировании алфавита.")

    result.write(bytearray(int_to_bins(len(filenames), 2)))
    begin_byte_of_files_information = result.tell()
    result.write(bytearray([0 for i in range(len(filenames) * 5)]))
    result.write(bytearray([i for i in compressor.pack_sequence()]))

    result.seek(begin_byte_of_files_information)
    _sizes_of_parts = compressor.get_sizes_of_parts()
    for i in range(len(filenames)):
        result.write(bytearray(int_to_bins(_sizes_of_parts[i], 4)))
        result.write(
            bytearray(int_to_bins(len(bytearray(os.path.basename(filenames[i]), encoding='utf-8')), 1)))

    for i in files:
        i.close()
    result.close()

    del compressor
