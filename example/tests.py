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

    def test_setter(self):
        a = Abel()
        a.justice = 11
        self.assertEqual(11, a.justice)
        with self.assertRaises(TypeError):
            a.justice = "Wrong type"

    def test_str(self):
        self.assertEqual("Abel(\"\")", str(Abel()))
        self.assertEqual("Kain(\"\")", str(Kain()))
        self.assertEqual("Abel(\"Bro\")", str(Abel("Bro")))
        self.assertEqual("Kain(\"Sis\")", str(Kain("Sis")))

    def test_spawn(self):
        self.assertIsInstance(Abel().spawn(), Kain)
        self.assertIsInstance(Kain().spawn(), Abel)
        self.assertEqual("Abel(\"from_TheSlayer\")", str(Kain("TheSlayer").spawn()))
        self.assertEqual("Kain(\"from_TheGoodOne\")", str(Abel("TheGoodOne").spawn()))
        self.assertEqual("Kain(1) slew Abel(2)", Kain("1", Abel("2")).slay())
        self.assertEqual("Kain(from_A) slew Abel(A)", Abel("A").spawn().slay())


if __name__ == "__main__":
    unittest.main()
