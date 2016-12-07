from .c_types import *

INDENT = "    "

def to_c_string(text):
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    text = text.replace('"', '\\"')
    return text

def indent_code(code, indent):
    import re
    return indent + re.sub(r"\n[ |\t]*", "\n"+indent, code.strip())



def render_struct(structtypename, struct_table, name, dictionary, indent="", first_line=""):
    name_width = 1
    type_width = 1
    for i in struct_table:
        name_width = max(name_width, len(i[0]))
        type_width = max(type_width, len(i[1]))

    code = "%(indent)sstatic %(type)s %(name)s =\n%(indent)s{\n" % {
        "indent": indent, "type": structtypename, "name": name
    }
    if first_line:
        code += indent + INDENT + first_line + "\n"
    for i in struct_table:
        code += "%(indent)s%(name)s %(type)s(%(value)s)" % {
            "indent": indent+INDENT,
            "name" : ("/* %s */" % i[0]).ljust(name_width + 6),
            "type" : ("(%s)" % i[1]).ljust(type_width + 13),
            "value" : str(dictionary.get(i[0], "NULL"))
        }
        if not i == struct_table[-1]:
            code += ","
        code += "\n"
    code += indent + "}; /* %s */\n" % name
    return code





class Renderer:
    """
    Main renderer for a module
    """
    def __init__(self, context):
        if not context:
            raise ValueError("No context given to Renderer")
        self.context = context
        self.namespaces = []
        self.h_header=""
        self.h_footer=""
        self.cpp_header=""
        self.cpp_footer=""

    @property
    def classes(self):
        return self.context.classes

    @property
    def functions(self):
        return self.context.functions

    @classmethod
    def write_to_file(self, filename, code):
        import codecs
        with codecs.open(filename, "w", "utf-8") as file:
            file.write(code)

    def render_hpp(self):
        code = """
        /* generated by cppy on %(date)s */

        %(header)s
        %(namespace_open)s

        %(init_types)s

        /* Call this before Py_Initialize() */
        bool initialize_module_%(name)s();

        %(namespace_close)s
        %(footer)s
        """
        init_types = ""
        for i in self.classes:
            init_types += "bool initialize_class_%s(void* pyObject_module);\n" % i.name
        import datetime
        code %= { "name": self.context.name,
                  "header": self.h_header, "footer": self.h_footer,
                  "date": datetime.datetime.now(),
                  "init_types": init_types,
                  "namespace_open": self._render_namespace_open(),
                  "namespace_close": self._render_namespace_close(),
                  }
        return code


    def render_cpp(self):
        code = """
        #include <python3.4/Python.h>
        #include <python3.4/structmember.h>

        #include <iostream>
        #define CPPY_ERROR(arg__) { std::cerr << arg__ << std::endl; }

        %(static_asserts)s

        %(namespace_open)s
        namespace {
        extern "C" {
        %(forwards)s
        } // extern "C"
        } // namespace
        %(namespace_close)s

        %(decl)s

        %(header)s

        %(namespace_open)s
        namespace {
        """
        code %= {
            "static_asserts" : self._render_static_asserts(),
            "header": self.context.format_cpp(self.cpp_header),
            "decl": self.context.format_cpp(self.context.cpp),
            "forwards": self._render_forwards(),
            "namespace_open": self._render_namespace_open(),
            "namespace_close": self._render_namespace_close(),
        }

        if self.functions:
            code += "\n/* #################### global functions ##################### */\n\n"
            code += 'extern "C" {\n'
            for i in self.functions:
                code += i.render_cpp_declaration()
            code += "\n" + self._render_method_struct()
            code += '} // extern "C"\n'

        if self.classes:
            for i in self.classes:
                code += "\n/* #################### class %s ##################### */\n\n" % i.name
                code += i.render_cpp_declaration()

        if self.context.cpp2:
            code += "\n" + self.context.format_cpp(self.context.cpp2) + "\n"

        code += '\nextern "C" {\n'
        code += self._render_module_def()
        code += '} // extern "C"\n'
        code += "\n} // namespace\n"
        code += "\n" + self._render_module_init()
        code += "\n" + self._render_namespace_close()
        code += "\n" + self.cpp_footer
        return code


    def _render_static_asserts(self):
        code = "#include <type_traits>\n"
        for functype in FUNCTIONS:
            params = FUNCTIONS[functype]
            parstr = params[1][0]
            for j in range(1, len(params[1])):
                parstr += ", %s" % params[1][j]
            typedef = "%(ret)s(*)(%(params)s)" % { "ret": params[0], "params": parstr }
            code += 'static_assert(std::is_same<%s,\n    %s>::value, "cppy/python api mismatch");\n' % (functype, typedef)
        return code

    def _render_forwards(self):
        code = ""
        for i in self.classes:
            code += "\n" + i.render_forwards()
        return code

    def _render_namespace_open(self):
        code = ""
        for i in self.namespaces:
            code += "namespace %s {\n" % i
        return code

    def _render_namespace_close(self):
        code = ""
        for i in reversed(self.namespaces):
            code += "} // namespace %s\n" % i
        return code

    def _render_module_init(self):
        code = """
        namespace {
            PyMODINIT_FUNC create_module_func()
            {
                auto module = PyModule_Create(&%(module_def)s);
                if (!module)
                    return nullptr;

                // add the classes
        %(init_calls)s

                return module;
            }
        } // namespace

        bool initialize_module_%(name)s()
        {
            PyImport_AppendInittab("%(name)s", create_module_func);
            return true;
        }
        """
        init_calls = ""
        for i in self.classes:
            init_calls += "        initialize_class_%s(module);\n" % i.name

        code %= {
            "name": self.context.name,
            "module_def": self.context.struct_name,
            "init_calls": init_calls
        }

        return code

    def _render_module_def(self):
        code = """
        static const char* %(doc_name)s = "%(doc)s";
        /* module definition for '%(name)s' */
        static PyModuleDef %(struct_name)s =
        {
            PyModuleDef_HEAD_INIT,
            "%(name)s",
            %(doc_name)s,
            -1, /* m_size */
            %(methods)s, /* m_methods */
            nullptr, /* m_reload */
            nullptr, /* m_traverse */
            nullptr, /* m_clear */
            nullptr, /* m_free */
        };
        """
        dic = { "name": self.context.name,
                "struct_name": self.context.struct_name,
                "doc_name": "%s_doc" % self.context.struct_name,
                "methods" : "nullptr",
                "doc": to_c_string(self.context.doc) }
        if len(self.functions):
            dic.update({ "methods": "reinterpret_cast<PyMethodDef*>(%s)" % self.method_struct_name})
        code %= dic
        return code

    def _render_method_struct(self):
        code = "static PyMethodDef %s[] =\n{\n" % self.context.method_struct_name
        for i in self.functions:
            code += "    " + i.render_cpp_member_struct_entry()
        code += "\n    { NULL, NULL, 0, NULL }\n};\n"
        return code
