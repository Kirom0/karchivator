import argparse
from pathlib import Path
from karch import *

parser = argparse.ArgumentParser(description='This program is an archiver with its own data type .karch')
parser.add_argument('-u', '--unpack', type=str,
                    help="Path to archive. The program'll unzips the archive specified by this parameter")
parser.add_argument('-p', '--pack', type=str,
                    help="Name of new archive. The program'll zips the files specified after this parametr")
parser.add_argument('-s', '--sources', nargs='+', help="Files for archiving.")


def ask(st):
    print(st)
    ans = input().lower().split()
    return ans[0] == 'y'


def sources_to_path(*sources):
    def bfs(path):
        for x in path.iterdir():
            if x.is_dir():
                dirs.append(x)
            if x.is_file():
                result.add(x)

    sources = [Path(x).resolve() for x in sources]
    for i in sources:
        if not i.exists():
            raise Exception("Ошибка. Файла или директории {} не существует.".format(str(i.resolve())))
    result = set(x for x in sources if x.is_file())
    dirs = [x for x in sources if x.is_dir()]
    current_dirs = 0
    while current_dirs < len(dirs):
        bfs(dirs[current_dirs])
        current_dirs += 1

    return list(result)


args = parser.parse_args()

if not ((args.pack is None) ^ (args.unpack is None)):
    exit("The program accepts only one parameter --pack or --unpack.")

if args.pack is not None:
    if args.pack[-6:] != ".karch":
        args.pack += ".karch"
    Coder.coder(ask, args.pack, *sources_to_path(*args.sources))

if args.unpack is not None:
    if args.unpack[-6:] != ".karch":
        args.unpack += ".karch"
    Decoder.decoder(args.unpack)
