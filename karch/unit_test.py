import unittest
import random
import os
import shutil
from pathlib import Path
from karch.Coder import coder
from karch.Decoder import decoder
from karch.__init__ import bins_to_int
from karch.__init__ import int_to_bins
from karch.__init__ import make_dir


class Test__init__methods(unittest.TestCase):
    def test_bins_to_int(self):
        self.assertEqual(200, bins_to_int([200]))
        self.assertEqual(256, bins_to_int([1, 0]))
        self.assertEqual(257, bins_to_int([0, 0, 1, 1]))
        self.assertEqual(255*256+255, bins_to_int([255, 255]))
        self.assertEqual(256*256, bins_to_int(bytes([1, 0, 0])))

    def test_int_to_bins(self):
        self.assertEqual([5], int_to_bins(5, 1))
        self.assertEqual([0, 0, 0, 0, 127], int_to_bins(127, 5))
        self.assertEqual([0, 0, 107, 39], int_to_bins(27431, 4))

    def test_bti_and_itb_interaction(self):
        for i in range(100):
            _len = random.randint(1, 8)
            value = random.randint(0, 256**_len - 1)
            self.assertEqual(value, bins_to_int(int_to_bins(value, _len)))

    def test_make_dir(self):
        main_dir = "test_make_dir"
        path = Path(main_dir)
        path.mkdir()
        path1 = path / "dir1" / "dir2" / "file.txt"
        make_dir(path1)
        path2 = path / "dir1" / "dir3" / "dir4" / "file.txt"
        make_dir(path2)
        self.assertTrue(path1.parent.exists())
        self.assertTrue(path2.parent.exists())
        shutil.rmtree(main_dir)

def asker(s):
    return True

def generate_file(pure_path):
    make_dir(pure_path)
    data = bytearray()
    for i in range(random.randint(100, 10**5)):
        data += bytes([random.randint(0, 255)])
    with pure_path.open("wb") as f:
        f.write(data)

class Test_Coder_and_Decoder(unittest.TestCase):
    def test_full(self):
        arch_clear_name = "Test_Coder_and_Decoder_full"
        arch_name = arch_clear_name + ".karch"
        files = []
        files.append(Path("test_full1.bin"))
        files.append(Path("test_full") / Path("file2.bin"))
        files.append(Path("test_full") / Path("file3.bin"))
        files.append(Path("test_full") / Path("folder") / Path("file4.bin"))

        for i in range(len(files)):
            generate_file(files[i])
            files[i] = files[i].resolve()

        coder(asker, arch_name, *files)
        decoder(arch_name)

        arch_dir = Path(arch_clear_name)
        self.assertTrue(arch_dir.exists())
        for f in files:
            _file = arch_dir / f
            self.assertTrue(_file.exists())
            self.assertEqual(f.read_bytes(), _file.read_bytes())
        shutil.rmtree(arch_clear_name)
        shutil.rmtree("test_full")
        os.remove("test_full1.bin")
        os.remove(arch_name)

