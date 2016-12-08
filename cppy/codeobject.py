
class CodeObject:
    """Base class of 'python things' that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.context = None
        self.name = name
        self.doc = doc if doc else ""
        self.src_pos = src_pos
        self.cpp = ""
        self.module = None

        cpp = self.doc.split("_CPP_:")
        if len(cpp) > 1:
            self.doc = cpp[0]
            self.cpp = cpp[1]

    def __str__(self):
        return "%s" % self.name

    def push_indent(self): self.context.push_indent()
    def pop_indent(self): self.context.pop_indent()
    def indent(self): return self.context.indent()
    def indent_length(self): return self.context.indent_length()
    def format_code(self, code): return self.context.format_cpp(code)

    def get_cpp(self):
        return self.context.format_cpp(self.cpp) if self.cpp else ""

    def render_cpp_declaration(self):
        raise NotImplementedError

