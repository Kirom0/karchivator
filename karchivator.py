import argparse
import os
from Karch import Karch

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


args = parser.parse_args()

if not ((args.pack is None) ^ (args.unpack is None)):
    exit("The program accepts only one parameter --pack or --unpack.")

if args.pack is not None:
    if args.pack[-6:] != ".karch":
        args.pack += ".karch"
    Karch.Coder(ask, args.pack, *args.sources)

if args.unpack is not None:
    if args.unpack[-6:] != ".karch":
        args.unpack += ".karch"
    Karch.Decoder(args.unpack)


