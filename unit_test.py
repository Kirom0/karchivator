import os
import unittest
import shutil
import Karchivator
from pathlib import Path
from karch.__init__ import make_dir


class Test_Sources_to_path(unittest.TestCase):
    def test(self):
        main_dir = Path("Test_main_dir")
        files = []
        files.append(main_dir / Path("dir1") / Path("dir1_1") / Path("file1.txt"))
        files.append(main_dir / Path("dir1") / Path("dir1_1") / Path("file2.txt"))
        files.append(main_dir / Path("dir1") / Path("dir1_2") / Path("file3.txt"))
        files.append(main_dir / Path("dir1") / Path("dir1_3") / Path("file4.txt"))
        files.append(main_dir / Path("dir2") / Path("dir2_1") / Path("file5.txt"))
        files.append(main_dir / Path("dir2") / Path("dir2_1") / Path("file6.txt"))
        files.append(main_dir / Path("dir2") / Path("file7.txt"))
        files.append(main_dir / Path("dir2") / Path("file8.txt"))
        files.append(main_dir / Path("dir2") / Path("dir2_2") / Path("file9.txt"))
        files.append(main_dir / Path("dir2") / Path("dir2_3") / Path("file10.txt"))
        files.append(main_dir / Path("dir2") / Path("dir2_4") / Path("file11.txt"))
        files.append(main_dir / Path("file12.txt"))
        files.append(Path("file13.txt"))

        for i in range(len(files)):
            make_dir(files[i])
            files[i].write_bytes(bytes(1))
            files[i] = files[i].resolve()

        self.assertEqual(frozenset(files), frozenset(Karchivator.sources_to_path("file13.txt", main_dir)))
        shutil.rmtree(main_dir)
        os.remove("file13.txt")
