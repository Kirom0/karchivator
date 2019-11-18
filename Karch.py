import os
from Compressor import Compressor
from Compressor import div_up


class Karch:
    @staticmethod
    def int_to_bins(value, size):
        res = []
        t = value
        for i in range(size):
            res.append(t % 256)
            t //= 256
        return res[::-1]

    @staticmethod
    def bins_to_int(value):
        res = 0
        category = 1
        for i in range(len(value) - 1, -1, -1):
            res += value[i] * category
            category *= 256
        return res

    @staticmethod
    def Coder(asker, result_filename, *filenames):
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

        coder = Compressor.Coder()
        for i in range(len(filenames)):
            coder.append_data(file_data_gen(filenames[i], files[i]))

        # Запись таблицы для декодирования
        encoded_keys = coder.encode_keys()
        try:
            result.write(bytearray(encoded_keys))
        except:
            raise Exception("Ошибка. Ошибка при кодировании алфавита.")

        result.write(bytearray(Karch.int_to_bins(len(filenames), 2)))
        begin_byte_of_files_information = result.tell()
        result.write(bytearray([0 for i in range(len(filenames) * 5)]))
        result.write(bytearray([i for i in coder.pack_sequence()]))

        result.seek(begin_byte_of_files_information)
        _sizes_of_parts = coder.get_sizes_of_parts()
        for i in range(len(filenames)):
            result.write(bytearray(Karch.int_to_bins(_sizes_of_parts[i], 4)))
            result.write(
                bytearray(Karch.int_to_bins(len(bytearray(os.path.basename(filenames[i]), encoding='utf-8')), 1)))

        for i in files:
            i.close()
        result.close()

        del coder

    @staticmethod
    def Decoder(archive_name):
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
        decoder = Compressor.Decoder()
        print("Reading...")
        data = arch.read()
        count = decoder.decode_keys(data)

        arch.seek(count + 5)
        count_of_files = Karch.bins_to_int(bytearray(arch.read(2)))
        parts = []
        names = []
        for i in range(count_of_files):
            parts.append(Karch.bins_to_int(bytearray(arch.read(4))))
            names.append(Karch.bins_to_int(bytearray(arch.read(1))))

        decoder.set_sizes_of_parts(parts)
        parts = [0] + parts
        data = data[count + 2 + 5 * count_of_files:]

        os.system("mkdir {} 2> /dev/null".format(os.path.splitext(archive_name)[0]))
        _dir = bytearray(os.path.splitext(archive_name)[0] + '/', encoding="utf-8")
        for i in range(count_of_files):
            print("Unpacking file #{}".format(i))
            archive_name = bytearray(decoder.unpack_sequence(data, i))
            print("Writing file #{}".format(i))
            with open((_dir + archive_name[:names[i]]).decode('utf-8'), 'wb') as f:
                f.write(archive_name[names[i]:])

        del decoder
