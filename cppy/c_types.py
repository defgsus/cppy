
"""
CPython's function pointers as dict:
typename: (return_type, (args,..))
"""
FUNCTIONS = {
    "unaryfunc":            ("PyObject*",   ("PyObject*",)),
    "binaryfunc":           ("PyObject*",   ("PyObject*", "PyObject*")),
    "ternaryfunc":          ("PyObject*",   ("PyObject*", "PyObject*", "PyObject*")),
    "inquiry":              ("int",         ("PyObject*",)),
    "lenfunc":              ("Py_ssize_t",  ("PyObject*",)),
    "ssizeargfunc":         ("PyObject*",   ("PyObject*", "Py_ssize_t")),
    "ssizessizeargfunc":    ("PyObject*",   ("PyObject*", "Py_ssize_t", "Py_ssize_t")),
    "ssizeobjargproc":      ("int",         ("PyObject*", "Py_ssize_t", "PyObject*")),
    "ssizessizeobjargproc": ("int",         ("PyObject*", "Py_ssize_t", "Py_ssize_t", "PyObject*")),
    "objobjargproc":        ("int",         ("PyObject*", "PyObject*", "PyObject*")),
    "freefunc":             ("void",        ("void*",)),
    "destructor":           ("void",        ("PyObject*",)),
    "printfunc":            ("int",         ("PyObject*", "FILE*", "int")),
    "getattrfunc":          ("PyObject*",   ("PyObject*", "char*")),
    "getattrofunc":         ("PyObject*",   ("PyObject*", "PyObject*")),
    "setattrfunc":          ("int",         ("PyObject*", "char*", "PyObject*")),
    "setattrofunc":         ("int",         ("PyObject*", "PyObject*", "PyObject*")),
    "reprfunc":             ("PyObject*",   ("PyObject*",)),
    "hashfunc":             ("Py_hash_t",   ("PyObject*",)),
    "richcmpfunc":          ("PyObject*",   ("PyObject*", "PyObject*", "int")),
    "getiterfunc":          ("PyObject*",   ("PyObject*",)),
    "iternextfunc":         ("PyObject*",   ("PyObject*",)),
    "descrgetfunc":         ("PyObject*",   ("PyObject*", "PyObject*", "PyObject*")),
    "descrsetfunc":         ("int",         ("PyObject*", "PyObject*", "PyObject*")),
    "initproc":             ("int",         ("PyObject*", "PyObject*", "PyObject*")),
    "newfunc":              ("PyObject*",   ("struct _typeobject*", "PyObject*", "PyObject*")),
    "allocfunc":            ("PyObject*",   ("struct _typeobject*", "Py_ssize_t")),
}



"""
All members of PyTypeObject (member_name, type)
"""
PyTypeObject = [
    ("tp_name",             "const char*"),
    ("tp_basicsize",        "Py_ssize_t"),
    ("tp_itemsize",         "Py_ssize_t"),
    ("tp_dealloc",          "destructor"),
    ("tp_print",            "printfunc"),
    ("tp_getattr",          "getattrfunc"),
    ("tp_setattr",          "setattrfunc"),
    ("tp_reserved",         "void*"),
    ("tp_repr",             "reprfunc"),
    ("tp_as_number",        "PyNumberMethods*"),
    ("tp_as_sequence",      "PySequenceMethods*"),
    ("tp_as_mapping",       "PyMappingMethods*"),
    ("tp_hash",             "hashfunc"),
    ("tp_call",             "ternaryfunc"),
    ("tp_str",              "reprfunc"),
    ("tp_getattro",         "getattrofunc"),
    ("tp_setattro",         "setattrofunc"),
    ("tp_as_buffer",        "PyBufferProcs*"),
    ("tp_flags",            "unsigned long"),
    ("tp_doc",              "const char*"),
    ("tp_traverse",         "traverseproc"),
    ("tp_clear",            "inquiry"),
    ("tp_richcompare",      "richcmpfunc"),
    ("tp_weaklistoffset",   "Py_ssize_t"),
    ("tp_iter",             "getiterfunc"),
    ("tp_iternext",         "iternextfunc"),
    ("tp_methods",          "struct PyMethodDef*"),
    ("tp_members",          "struct PyMemberDef*"),
    ("tp_getset",           "struct PyGetSetDef*"),
    ("tp_base",             "struct _typeobject*"),
    ("tp_dict",             "PyObject*"),
    ("tp_descr_get",        "descrgetfunc"),
    ("tp_descr_set",        "descrsetfunc"),
    ("tp_dictoffset",       "Py_ssize_t"),
    ("tp_init",             "initproc"),
    ("tp_alloc",            "allocfunc"),
    ("tp_new",              "newfunc"),
    ("tp_free",             "freefunc"),
    ("tp_is_gc",            "inquiry"),
    ("tp_bases",            "PyObject*"),
    ("tp_mro",              "PyObject*"),
    ("tp_cache",            "PyObject*"),
    ("tp_subclasses",       "PyObject*"),
    ("tp_weaklist",         "PyObject*"),
    ("tp_del",              "destructor"),
    ("tp_version_tag",      "unsigned int"),
    ("tp_finalize",         "destructor"),
]

PyNumberMethods = [
    ("nb_add",                  "binaryfunc"),
    ("nb_subtract",             "binaryfunc"),
    ("nb_multiply",             "binaryfunc"),
    ("nb_remainder",            "binaryfunc"),
    ("nb_divmod",               "binaryfunc"),
    ("nb_power",                "ternaryfunc"),
    ("nb_negative",             "unaryfunc"),
    ("nb_positive",             "unaryfunc"),
    ("nb_absolute",             "unaryfunc"),
    ("nb_bool",                 "inquiry"),
    ("nb_invert",               "unaryfunc"),
    ("nb_lshift",               "binaryfunc"),
    ("nb_rshift",               "binaryfunc"),
    ("nb_and",                  "binaryfunc"),
    ("nb_xor",                  "binaryfunc"),
    ("nb_or",                   "binaryfunc"),
    ("nb_int",                  "unaryfunc"),
    ("nb_reserved",             "void*"),
    ("nb_float",                "unaryfunc"),
    ("nb_inplace_add",          "binaryfunc"),
    ("nb_inplace_subtract",     "binaryfunc"),
    ("nb_inplace_multiply",     "binaryfunc"),
    ("nb_inplace_remainder",    "binaryfunc"),
    ("nb_inplace_power",        "ternaryfunc"),
    ("nb_inplace_lshift",       "binaryfunc"),
    ("nb_inplace_rshift",       "binaryfunc"),
    ("nb_inplace_and",          "binaryfunc"),
    ("nb_inplace_xor",          "binaryfunc"),
    ("nb_inplace_or",           "binaryfunc"),
    ("nb_floor_divide",         "binaryfunc"),
    ("nb_true_divide",          "binaryfunc"),
    ("nb_inplace_floor_divide", "binaryfunc"),
    ("nb_inplace_true_divide",  "binaryfunc"),
    ("nb_index",                "unaryfunc"),
]

PySequenceMethods = [
    ("sq_length",           "lenfunc"),
    ("sq_concat",           "binaryfunc"),
    ("sq_repeat",           "ssizeargfunc"),
    ("sq_item",             "ssizeargfunc"),
    ("was_sq_slice",        "void*"),
    ("sq_ass_items",        "ssizeobjargproc"),
    ("was_sq_ass_slice",    "void*"),
    ("sq_contains",         "objobjproc"),
    ("sq_inplace_concat",   "binaryfunc"),
    ("sq_inplace_repeat",   "ssizeargfunc"),
]

PyMappingMethods = [
    ("mp_length",           "lenfunc"),
    ("mp_subscript",        "binaryfunc"),
    ("mp_ass_subscript",    "objobjargproc"),
]

PyBufferProcs = [
    ("bf_getbuffer",        "getbufferproc"),
    ("bf_releasebuffer",    "releasebufferproc"),
]



SEQUENCE_FUNCS = [
    ("__len__", "sq_length", "lenfunc"),
    ("__???__", "sq_concat", "binaryfunc"),
    ("__???__", "sq_repeat", "ssizeargfunc"),
    ("__getitem__", "sq_item", "ssizeargfunc"),
    ("__???___", "was_sq_slice", "void*"),
    ("__setitem__", "sq_ass_item", "ssizeobjargproc"),
    ("__???___", "was_sq_ass_slice", "void*"),
    ("__contains__", "sq_contains", "objobjproc"),
    ("__???___", "sq_inplace_concat", "binaryfunc"),
    ("__???___", "sq_inplace_repeat", "ssizeargfunc"),
]

NUMBER_FUNCS = [
    ("__add__", "nb_add", "binaryfunc"),
    ("__sub__", "nb_subtract", "binaryfunc"),
    ("__mul__", "nb_multiply", "binaryfunc"),
    ("__???__", "nb_remainder", "binaryfunc"),
    ("__???__", "nb_divmod", "binaryfunc"),
    ("__pow__", "nb_power", "ternaryfunc"),
    ("__neg__", "nb_negative", "unaryfunc"),
    ("__pos__", "nb_positive", "unaryfunc"),
    ("__abs__", "nb_absolute", "unaryfunc"),
    ("__bool__", "nb_bool", "inquiry"),
    ("__???__", "nb_invert", "unaryfunc"),
    ("__???__", "nb_lshift", "binaryfunc"),
    ("__???__", "nb_rshift", "binaryfunc"),
    ("__and__", "nb_and", "binaryfunc"),
    ("__xor__", "nb_xor", "binaryfunc"),
    ("__or__", "nb_or", "binaryfunc"),
    ("__???__", "nb_int", "unaryfunc"),
    ("__???__", "nb_reserved", "void*"),
    ("__???__", "nb_float", "unaryfunc"),
    ("__iadd__", "nb_inplace_add", "binaryfunc"),
    ("__isub__", "nb_inplace_subtract", "binaryfunc"),
    ("__imul__", "nb_inplace_multiply", "binaryfunc"),
    ("__???___", "nb_inplace_remainder", "binaryfunc"),
    ("__ipow__", "nb_inplace_power", "ternaryfunc"),
    ("__???__", "nb_inplace_lshift", "binaryfunc"),
    ("__???__", "nb_inplace_rshift", "binaryfunc"),
    ("__iand__", "nb_inplace_and", "binaryfunc"),
    ("__ixor__", "nb_inplace_xor", "binaryfunc"),
    ("__ior__", "nb_inplace_or", "binaryfunc"),
    ("__floordiv__", "nb_floor_divide", "binaryfunc"),
    ("__truediv__", "nb_true_divide", "binaryfunc"),
    ("__ifloordiv__", "nb_inplace_floor_divide", "binaryfunc"),
    ("__itruediv__", "nb_inplace_true_divide", "binaryfunc"),
    ("__???__", "nb_index", "unaryfunc"),
]


SPECIAL_FUNCS = [
    ("__str__", "tp_str"),
    ("__repr__", "tp_repr"),
    ("__init__", "tp_init"),
]

# otherwise PyObject*
SPECIAL_RETURN_TYPES = {
    "__init__": "int",
    "__len__": "Py_ssize_t",
    "__setitem__": "int",
}
SPECIAL_ARGUMENTS = {
    "__getitem__": ", Py_ssize_t index",
    "__setitem__": ", Py_ssize_t index, PyObject* arg",
}
