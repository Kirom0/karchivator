import os
from Compressor import Compressor
from Compressor import div_up


def ask(st):
    print(st)
    ans = input().lower().split()
    return ans[0] == 'y'


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

    class Coder:
        def __init__(self, asker, result, *files):
            def file_data_gen(path, file):
                yield from bytearray(os.path.basename(path), encoding='utf-8')
                yield from file.read()

            self._files = []
            if os.path.exists(result):
                if not asker("Файл \"{}\" уже сущесвует. Перезаписать?".format(result)):
                    raise Exception("Ошибка. Отказ в записи.")
            for i in files:
                if not os.path.exists(i):
                    raise Exception("Ошибка. Файл \"{}\" не найден.".format(i))

            for i in files:
                try:
                    self._files.append(open(i, "rb"))
                except PermissionError:
                    raise Exception("Ошибка. Файл \"{}\" занят другим процессом.".format(i))
            self._result = open(result, "wb")

            # 5 байт - "karch"
            self._result.write(b"karch")

            self.coder = Compressor.Coder()
            for i in range(len(files)):
                self.coder.append_data(file_data_gen(files[i], self._files[i]))

            # 1 байт - Размер алфавита - n ... байт - Описание дерева ключей. Описание заканчивается, тогда когда в
            # нём встретилось n бит, равных единице n байт - Перечисление ключей, по одному ключу в каждом. Положение
            # ключа в описании дерева ключей соответсвует его порядку. (i-тая единица в дереве соотвествует i-тому
            # ключу)
            encoded_keys = self.coder.encode_keys()
            #print(encoded_keys)
            try:
                self._result.write(bytearray(encoded_keys))
            except:
                raise Exception("Ошибка. Ошибка при кодировании алфавита.")

            self._result.write(bytearray(Karch.int_to_bins(len(files), 2)))
            begin_byte_of_files_information = self._result.tell()
            self._result.write(bytearray([0 for i in range(len(files) * 5)]))
            self._result.write(bytearray([i for i in self.coder.pack_sequence()]))

            self._result.seek(begin_byte_of_files_information)
            self._sizes_of_parts = self.coder.get_sizes_of_parts()
            for i in range(len(files)):
                self._result.write(bytearray(Karch.int_to_bins(self._sizes_of_parts[i], 4)))
                self._result.write(
                    bytearray(Karch.int_to_bins(len(bytearray(os.path.basename(files[i]), encoding='utf-8')), 1)))

            for i in self._files:
                i.close()
            self._result.close()

    class Decoder:
        def __init__(self, file):
            def generator_of_list_part(mas, start_with, end_on):
                for i in range(start_with, end_on):
                    yield mas[i]

            if not os.path.exists(file):
                raise Exception("Ошибка. Файла \"{}\" не существует.".format(file))
            try:
                self._file = open(file, "rb")
            except PermissionError:
                raise Exception("Ошибка. Файл \"{}\" занят другим процессом".format(file))

            assert self._file.read(5) == b'karch'
            self.decoder = Compressor.Decoder()
            print("Reading...")
            data = self._file.read()
            count = self.decoder.decode_keys(data)

            self._file.seek(count + 5)
            count_of_files = Karch.bins_to_int(bytearray(self._file.read(2)))
            parts = []
            names = []
            for i in range(count_of_files):
                parts.append(Karch.bins_to_int(bytearray(self._file.read(4))))
                names.append(Karch.bins_to_int(bytearray(self._file.read(1))))

            self.decoder.set_sizes_of_parts(parts)
            parts = [0] + parts
            data = data[count + 2 + 5 * count_of_files:]
            
            os.system("mkdir {}".format(os.path.splitext(file)[0]))
            _dir = bytearray(os.path.splitext(file)[0] + '/', encoding="utf-8")
            for i in range(count_of_files):
                print("Unpacking file #{}".format(i))
                file = bytearray(self.decoder.unpack_sequence(data, i))
                print("Writing file #{}".format(i))
                with open((_dir + file[:names[i]]).decode('utf-8'), 'wb') as f:
                    f.write(file[names[i]:])


if __name__ == "__main__":
    #cd = Karch.Coder(ask, "second.karch", "xt.txt", "ttx.txt")
    #d = Karch.Decoder("second.karch")
    pass
