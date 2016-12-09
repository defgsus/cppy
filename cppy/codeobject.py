from .renderer import split_doc_cpp

class CodeObject:
    """Base class of 'python things' that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.context = None
        self.name = name
        self.src_pos = src_pos
        self.module = None
        self.doc, self._cpp = split_doc_cpp(doc) if doc else ("", {})

    def __str__(self):
        return "%s" % self.name

    def push_indent(self): self.context.push_indent()
    def pop_indent(self): self.context.pop_indent()
    def indent(self): return self.context.indent()
    def indent_length(self): return self.context.indent_length()
    def format_code(self, code): return self.context.format_cpp(code, self)

    def render_forward_decl(self):
        """Stuff that needs to be known by all other code"""
        return ""

    def render_impl_decl(self):
        """Implementation that need final definition of all type structs, etc.."""
        return ""


    def has_cpp(self, key=None):
        return True if key in self._cpp and self._cpp[key] else False

    def cpp(self, key=None, formated=True):
        if formated:
            return self.format_code(self._cpp[key]) if key in self._cpp else ""
        else:
            return self._cpp[key] if key in self._cpp else ""

    def render_cpp_declaration(self):
        raise NotImplementedError

