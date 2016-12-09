import unittest
import example as ex

class TestExample(unittest.TestCase):

    def test_functions(self):
        self.assertEqual(444., ex.func_a())
        self.assertEqual(5., ex.func_add(2,3))
        self.assertEqual(27., ex.func_add(13,14))

    def test_init(self):
        self.assertIsInstance(ex.Abel(), ex.Abel)
        self.assertIsInstance(ex.Kain(), ex.Kain)

    def _test_assignment(self, cls):
        self.assertEqual("", cls().get())
        self.assertEqual("Hallo", cls("Hallo").get())
        a = cls("Python")
        self.assertEqual("Python", a.get())
        a.set("fetzt")
        self.assertEqual("fetzt", a.get())

    def test_assignment(self):
        self._test_assignment(ex.Abel)
        self._test_assignment(ex.Kain)




if __name__ == "__main__":
    unittest.main()
