import os
from karch.compressor import *
from karch.__init__ import int_to_bins
from karch.__init__ import cut_common_dir
from karch.__init__ import calculate_file_hash
from karch.PackingInfo import PackingInfo
from console_progress import *


def coder(asker, result_filename, *filenames):
    """
    :param asker: функция, которая запрашивает у пользователя разрешения
    :param result_filename: имя архива
    :param filenames: список pure_paths с файлами, которые будут добавлены в архив. ПУТИ ТОЛЬКО АБСОЛЮТНЫЕ
    :result: Создает архив с именем  result_filename, с запакованными в нем файлами из списка filenames
    """
    def file_data_gen(pure_path):
        yield from bytearray(cut_common_dir(pure_path, common_ancestor_depth), encoding='utf-8')
        yield from pure_path.read_bytes()

    files = []
    if os.path.exists(result_filename):
        if not asker("Файл \"{}\" уже сущесвует. Перезаписать?".format(result_filename)):
            raise Exception("Ошибка. Отказ в записи.")

    for i in filenames:
        if not i.exists():
            raise Exception("Ошибка. Файл \"{}\" не найден.".format(i))

    for i in filenames:
        try:
            files.append(PackingInfo(i))
        except PermissionError:
            raise Exception("Ошибка. Файл \"{}\" занят другим процессом.".format(i))

    #Поиск наиглубнейшей общей папки, в которой находятся все файлы
    common_ancestor_depth = len(filenames[0].parents)
    common_ancestor_dir = filenames[0].parents[0]

    for i in filenames:
        while common_ancestor_depth > len(i.parents) or common_ancestor_dir != i.parents[len(i.parents) - common_ancestor_depth]:
            common_ancestor_depth -= 1
            common_ancestor_dir = filenames[0].parents[len(filenames[0].parents) - common_ancestor_depth]

    result = open(result_filename, "wb")



    # 5 байт - "karch"
    result.write(b"karch")

    compressor = Compressor.Compressor()
    work = ProgressBar.ProgressBar("Reading files", len(files))
    for i in range(len(files)):
        work.do_progress(i + 1)
        compressor.append_data(file_data_gen(files[i].file_pure_path))
    work.finish()

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

    for i in range(len(filenames)):
        files[i].compressed_size = compressor.result_bytes[i]

    result.seek(begin_byte_of_files_information)
    _sizes_of_parts = compressor.get_sizes_of_parts()
    for i in range(len(filenames)):
        result.write(bytearray(int_to_bins(_sizes_of_parts[i], 4)))
        result.write(
            bytearray(int_to_bins(len(bytearray(cut_common_dir(filenames[i], common_ancestor_depth), encoding='utf-8')), 1)))

    result.close()
    _hash = calculate_file_hash(result_filename, os.path.getsize(result_filename))
    with open(result_filename, "ab") as result:
        result.write(bytearray(int_to_bins(_hash, 4)))

    del compressor

    # Вывод информации о сжатии

    for i in files:
        print("Файл {}: {} байт -> {} байт. Компрессия {:.2f}%".format(cut_common_dir(i.file_pure_path, common_ancestor_depth), i.full_size, i.compressed_size, 100 - 100 * i.compressed_size / i.full_size))
    size_before = sum(x.full_size for x in files)
    size_after = os.path.getsize(result_filename)
    print("Суммарный исходный размер {} байт. Размер архива {} байт. Компрессия {:.2f}%".format(
        size_before,
        size_after,
        100 - 100 * size_after / size_before
    ))
