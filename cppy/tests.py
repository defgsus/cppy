import unittest
from cppy.renderer import *

class TestRenderer(unittest.TestCase):

    def test_strip_newline(self):
        self.assertEqual("bla\nblub", strip_newlines("\nbla\nblub\n"))
        self.assertEqual("bla\nblub", strip_newlines("  \nbla\nblub  \n  "))
        self.assertEqual("  bla\n  blub", strip_newlines("\n  bla\n  blub\n"))

    def test_change_text_indent(self):
        self.assertEqual("bla\nblub", change_text_indent("bla\nblub", 0))
        self.assertEqual("bla\nblub", change_text_indent("  bla\n  blub", 0))
        self.assertEqual("bla\n blub", change_text_indent("  bla\n   blub", 0))
        self.assertEqual(" bla\n blub", change_text_indent("bla\nblub", 1))
        self.assertEqual("   bla\n  blub", change_text_indent(" bla\nblub", 2))

    def test_apply_string_dict(self):
        dic = { "val": "value",
                "val2": "other",
                "multiline": "for x in range(10):\n    print(x)"
                }
        self.assertEqual("value", apply_string_dict("%(val)s", dic))
        self.assertEqual("  value", apply_string_dict("  %(val)s", dic))
        self.assertEqual("blub-value-bla", apply_string_dict("blub-%(val)s-bla", dic))
        self.assertEqual("blub-value.other-bla", apply_string_dict("blub-%(val)s.%(val2)s-bla", dic))
        self.assertEqual("void value::cppy_copy(value* copy)",
                         apply_string_dict("void %(val)s::cppy_copy(%(val)s* copy)", dic))
        self.assertEqual("func() {\n    value;\n}",
                         apply_string_dict("func() {\n    %(val)s;\n}", dic) )

        self.assertEqual("func() {\n    value;\n    other;\n}",
                         apply_string_dict("func() {\n    %(val)s;\n    %(val2)s;\n}", dic) )

        code = """def func(a):
    %(val)s = 10
    for i in a:
        %(val2)s[i] = %(val)s
        %(multiline)s
"""
        expect = """def func(a):
    value = 10
    for i in a:
        other[i] = value
        for x in range(10):
            print(x)
"""
        self.assertEqual(expect, apply_string_dict(code, dic))




if __name__ == "__main__":
    unittest.main()