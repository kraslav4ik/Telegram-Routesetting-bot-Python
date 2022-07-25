import unittest
from source.Storage import Storage


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.storage = Storage(path='../data/test_database_info')

    def test_storage_creation(self):
        pass

    def test_add_single_res(self):
        pass

    def test_add_setting(self):
        pass

    def test_add_setter(self):
        pass


if __name__ == '__main__':
    unittest.main()
