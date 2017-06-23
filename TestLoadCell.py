import unittest
from LoadCell import LoadCell


class TestLoadCell(unittest.TestCase):

    def test_class_exists(self):
        lc = LoadCell(5, 6)

    def test_msb_bits_to_int_min(self):
        lc = LoadCell(5, 6)
        self.assertEqual(lc._bits_to_int("000000000000000000000000"), 0)

    def test_msb_bits_to_int_max(self):
        lc = LoadCell(5, 6)
        self.assertEqual(lc._bits_to_int("111111111111111111111111"), 16777215)

    def test_get_reading(self):
        pass


if __name__ == '__main__':
    unittest.main()
