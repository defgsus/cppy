import unittest
from example import *

class TestExample(unittest.TestCase):

    def test_functions(self):
        self.assertEqual(444., func_a())
        self.assertEqual(5., func_add(2,3))
        self.assertEqual(27., func_add(13,14))

    def test_init(self):
        self.assertIsInstance(Abel(), Abel)
        self.assertIsInstance(Kain(), Kain)

    def _test_assignment(self, cls):
        self.assertEqual("", cls().get())
        self.assertEqual("Hallo", cls("Hallo").get())
        a = cls("Python")
        self.assertEqual("Python", a.get())
        a.set("fetzt")
        self.assertEqual("fetzt", a.get())

    def test_assignment(self):
        self._test_assignment(Abel)
        self._test_assignment(Kain)




if __name__ == "__main__":
    unittest.main()
