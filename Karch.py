import os
from Compressor import Compressor


def ask(st):
    print(st)
    ans = input().lower().split()
    return ans[0] == 'y'


class Karch:

    @staticmethod
    def int_to_bins(value, size):
        res = []
        for i in range(size):
            t = value // 256 ** i
            res.append(t % 256 ** (i + 1))
        return res[::-1]

    class Coder:
        def __init__(self, asker, result, *files):
            def file_data_gen(path, file):
                yield from bytearray(os.path.basename(path), encoding='ascii')
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
            try:
                self._result.write(bytearray(encoded_keys))
            except:
                raise Exception("Ошибка. Ошибка при кодировании алфавита.")

            begin_byte_of_files_information = self._result.tell()
            self._result.write(bytearray([0 for i in range(len(files) * 5)]))
            self._result.write(bytearray([i for i in self.coder.pack_sequence()]))
            #for i in self.coder.pack_sequence():
            #    self._result.write(i)

            self._result.seek(begin_byte_of_files_information)
            self._sizes_of_parts = self.coder.get_sizes_of_parts()
            for i in range(len(files)):
                self._result.write(bytearray(Karch.int_to_bins(self._sizes_of_parts[i], 4)))
                self._result.write(
                    bytearray(Karch.int_to_bins(len(bytearray(os.path.basename(files[i]), encoding='ascii')), 1)))



        def close(self):
            for i in self._files:
                i.close()
            self._result.close()

    class Decoder:
        pass


if __name__ == "__main__":
    cd = Karch.Coder(ask, "first.karch", "one.txt")
    cd.close()
