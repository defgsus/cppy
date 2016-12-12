from .renderer import split_doc_cpp

class DocObject:
    def __init__(self, doc):
        self.doc, self._cpp = split_doc_cpp(doc) if doc else ("", {})
        for key in self._cpp:
            if not key in self.supported_doc_tags():
                raise RuntimeError("CPP annotation tag '%s' not supported by %s" % (str(key), str(self)))

    def has_cpp(self, key=None):
        return True if key in self._cpp and self._cpp[key] else False

    def cpp(self, key=None, formated=True):
        if formated:
            return self.format_code(self._cpp[key]) if key in self._cpp else ""
        else:
            return self._cpp[key] if key in self._cpp else ""

    def format_code(self, code):
        raise NotImplementedError

    def supported_doc_tags(self):
        """Return a list if strings"""
        raise NotImplementedError


class CodeObject(DocObject):
    """Base class of 'python things' that have a cpp representation"""
    def __init__(self, name, doc="", src_pos=""):
        self.name = name
        self.src_pos = src_pos
        super(CodeObject, self).__init__(doc)
        self.module = None
        self.context = None

    def __str__(self):
        return "%s" % self.name

    def format_code(self, code):
        return self.context.format_cpp(code, self)

    def render_header_forwards(self):
        """Stuff that needs to be known by all other code in the .h file"""
        raise NotImplementedError

    def render_header_impl(self):
        """Stuff that implements stuff in the .h file"""
        raise NotImplementedError

    def render_forwards(self):
        """Stuff that needs to be known by all other code in .cpp file"""
        raise NotImplementedError

    def render_impl(self):
        """Implementation that need final definition of all type structs, etc.."""
        raise NotImplementedError

    def render_python_api(self):
        """The general python c-api constructs"""
        raise NotImplementedError
