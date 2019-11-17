##Разметка файла формата .karch:
* 5 байт - "karch"
* 1 байт - Размер алфавита - n
* ... байт - Описание дерева ключей. Описание заканчивается, тогда когда в нём встретилось n бит, равных единице
* n байт - Перечисление ключей, по одному ключу в каждом. Положение ключа в описании дерева ключей соответсвует его порядку. (i-тая единица в дереве соотвествует i-тому ключу)
* 2 байта - Количество архивированных файлов - m
* m блоков по 5 байт:
    * 4 байта - размер i-того сжатого файла в битах
    * 1 байт - рамер имени файла
* ... байт (До конца файла) - заархивированные данные. Порядок сжатых файлов в нём сохранён. 

