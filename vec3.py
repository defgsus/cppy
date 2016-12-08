import math

__doc__ = """
_CPP_:
#include "vector_helper.h"
#include "io/log.h"

#define MO__VEC_OP_COPY(op__, op_rev__) \
    PyObject* left = (PyObject*)self, *right = (PyObject*)arg1; \
    bool reversed = false; \
    if (!$IS_INSTANCE(left, vec3)) \
        { std::swap(left, right); reversed = true; }\
    if (!$IS_INSTANCE(left, vec3)) \
        { setPythonError(PyExc_TypeError, \
                QString("Illegal arguments to binary operator, '%1' and '%2'") \
                .arg(typeName(arg0)).arg(typeName(arg1))); } \
    self = ($STRUCT(vec3)*)left; \
    auto ret = $COPY(self, vec3); \
    if (reversed) \
        { if (vectorBinaryOpInplace(ret, right, [](double& l, double r){ op_rev__; })) return (PyObject*)ret; } \
    else \
        if (vectorBinaryOpInplace(ret, right, [](double& l, double r){ op__; })) return (PyObject*)ret; \
    Py_DECREF(ret); \
    return NULL;

#define MO__VEC_OP_INPLACE(op__) \
    if (vectorBinaryOpInplace(self, arg1, [](double& l, double r){ op__; })) \
        Py_RETURN_SELF; \
    else \
        return NULL;

_CPP_:
#undef MO__VEC_OP_COPY
#undef MO__VEC_OP_INPLACE

"""

class vec3:
    """
    Class vec3 implementation.
    It behaves like a list of floats of length 3
    Arguments to member functions can be any list-like objects,
    typically of length 3 as well, containing float-convertible elements
    _CPP_:
    static constexpr size_t len = 3;
    double v[3];
    double length() const { return std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]); }

    void cppy_copy($STRUCT(vec3)* copy)
    {
        for (size_t i=0; i<len; ++i)
            copy->v[i] = this->v[i];
    }
    """

    def __init__(self, arg=None):
        """
        _CPP_:
        if (auto o = vectorSet(self, arg1))
        {
            Py_DECREF(o);
            return 0;
        }
        return 1;
        """
        if arg is None:
            self.v = [0., 0., 0.]
            return
        self.set(arg)

    def __str__(self):
        """
        _CPP_:
        return toPython(QString("vec3(%1, %2, %3)").arg(self->v[0]).arg(self->v[1]).arg(self->v[2]));
        """
        return "vec3(%g, %g, %g)" % (self.v[0], self.v[1], self.v[2])

    def __repr__(self):
        """
        _CPP_:
        return toPython(QString("vec3@%1(%2, %3, %4)").arg((size_t)self, 0, 16)
                        .arg(self->v[0]).arg(self->v[1]).arg(self->v[2]) );
        """
        return self.__str__()

    # ---- x,y,z properties ----

    @property
    def x(self):
        """
        _CPP_: return toPython(self->v[0]);
        _CPP_: double v; if (!fromPython(arg1, &v)) return 1; self->v[0] = v; return 0;
        """
        return self.v[0]
    @x.setter
    def x(self, arg):
        self.v[0] = float(arg)

    @property
    def y(self):
        """
        The y component
        _CPP_: return toPython(self->v[1]);
        _CPP_: double v; if (!fromPython(arg1, &v)) return 1; self->v[1] = v; return 0;
        """
        return self.v[1]
    @y.setter
    def y(self, arg):
        self.v[1] = float(arg)

    @property
    def z(self):
        """
        _CPP_: return toPython(self->v[2]);
        _CPP_: double v; if (!fromPython(arg1, &v)) return 1; self->v[2] = v; return 0;
        """
        return self.v[2]
    @z.setter
    def z(self, arg):
        self.v[2] = float(arg)

    # --- list-like ---

    def __len__(self):
        """
        _CPP_:
        CPPY_UNUSED(self);
        return 3;
        """
        return 3

    def __iter__(self):
        return self.v.__iter__()

    def __getitem__(self, item):
        """
        _CPP_:
        if (!checkIndex(arg1, self->len))
            return NULL;
        return toPython(self->v[arg1]);
        """
        return self.v[item]

    def __setitem__(self, key, value):
        """
        _CPP_:
        double val;
        if (!checkIndex(arg1, self->len) || !expectFromPython(arg2, &val))
            return 1;
        self->v[arg1] = val;
        return 0;
        """
        self.v[key] = float(value)

    def __contains__(self, item):
        return item in self.v

    # --- boolean equality ---

    def __eq__(self, other):
        """
        :param other: float sequence of length 3
        :return: True or False
        _CPP_:
        MO_PRINT("RICHCOMP " << arg2);
        double v[self->len];
        if (!expectFromPythonSequence(arg1, v, self->len))
            return NULL;
        for (size_t i=0; i<self->len; ++i)
            if (self->v[i] != v[i])
                Py_RETURN_FALSE;
        Py_RETURN_TRUE;
        """
        if isinstance(other, vec3):
            return self.v == other.v
        tools.check_float_sequence(other)
        if not len(other) == len(self):
            return False
        for i in range(len(self)):
            if not self.v[i] == other[i]:
                return False
        return True

    ## --- classic math ops ---

    def __abs__(self):
        return vec3([abs(x) for x in self.v])

    def __neg__(self):
        return vec3([-x for x in self.v])

    def __round__(self, n=None):
        if n is None:
            return vec3([float(round(x)) for x in self.v])
        else:
            return vec3([float(round(x, n)) for x in self.v])

    # ------- arithmetic ops --------

    def __add__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_COPY(l += r, l = r + l)
        """
        return self._binary_operator(arg, lambda l, r: l + r)

    def __radd__(self, arg):
        return self._binary_operator_inplace(arg, lambda r, l: l + r)

    def __iadd__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_INPLACE(l += r)
        """
        return self._binary_operator_inplace(arg, lambda l, r: l + r)


    def __sub__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_COPY(l -= r, l = r - l)
        """
        return self._binary_operator(arg, lambda l, r: l - r)

    def __rsub__(self, arg):
        return self._binary_operator(arg, lambda r, l: l - r)

    def __isub__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_INPLACE(l -= r)
        """
        return self._binary_operator_inplace(arg, lambda l, r: l - r)


    def __mul__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_COPY(l *= r, l = r * l)
        """
        return self._binary_operator(arg, lambda l, r: l * r)

    def __rmul__(self, arg):
        return self._binary_operator(arg, lambda r, l: l * r)

    def __imul__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_INPLACE(l *= r)
        """
        return self._binary_operator_inplace(arg, lambda l, r: l * r)


    def __truediv__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_COPY(l /= r, l = r / l)
        """
        return self._binary_operator(arg, lambda l, r: l / r)

    def __rtruediv__(self, arg):
        return self._binary_operator(arg, lambda r, l: l / r)

    def __itruediv__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_INPLACE(l /= r)
        """
        return self._binary_operator_inplace(arg, lambda l, r: l / r)


    def __mod__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_COPY(l = std::fmod(l, r), l = std::fmod(r, l))
        """
        return self._binary_operator(arg, lambda l, r: l % r)

    def __rmod__(self, arg):
        return self._binary_operator(arg, lambda r, l: l % r)

    def __imod__(self, arg):
        """
        _CPP_:
        MO__VEC_OP_INPLACE(l = std::fmod(l, r))
        """
        return self._binary_operator_inplace(arg, lambda l, r: l % r)

    # --- op helper ---

    def _binary_operator(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            return vec3([op(x, fother) for x in self.v])
        tools.check_float_sequence(arg, len(self))
        return vec3([op(x, float(arg[i])) for i, x in enumerate(self.v)])

    def _binary_operator_inplace(self, arg, op):
        if tools.is_number(arg):
            fother = float(arg)
            for i in range(len(self)):
                self.v[i] = op(self.v[i], fother)
            return self
        tools.check_float_sequence(arg, len(self))
        for i in range(len(self)):
            self.v[i] = op(self.v[i], float(arg[i]))
        return self

    # --- public API ---

    def set(self, arg):
        """
        Set the values of this vector
        :param arg: float number or sequence
        :return: self

        >>> vec3(1)
        vec3(1, 1, 1)
        >>> vec3((1,2))
        vec3(1, 2, 0)
        >>> vec3([1,2,3])
        vec3(1, 2, 3)
        _CPP_:
        return vectorSet(self, arg1);
        """
        if tools.is_number(arg):
            arg = float(arg)
            self.v = [arg, arg, arg]
            return self

        tools.check_float_sequence(arg)

        if len(arg) > len(self):
            raise TypeError("Sequence %s with length %d is too long for %s" % (type(arg), len(arg), type(self)))

        if len(arg) == len(self):
            self.v = [float(x) for x in arg]
            return self

        self.v = [x for x in arg]
        for i in range(len(self) - len(arg)):
            self.v.append(0.)

    def copy(self):
        """
        Returns a copy of the vector
        :return: new vec3
        _CPP_:
        return (PyObject*)$COPY(self, vec3);
        """

    # ----- getter -----

    def length(self):
        """
        Returns cartesian length of vector
        :return: float
        >>> vec3((5,0,0)).length()
        5.0
        >>> vec3(1).length() == math.sqrt(3.)
        True
        _CPP_:
        return toPython(std::sqrt(self->v[0]*self->v[0] + self->v[1]*self->v[1] + self->v[2]*self->v[2]));
        """
        return math.sqrt(sum([x*x for x in self.v]))

    def length_squared(self):
        """
        Returns the square of the cartesian length of vector
        :return: float
        >>> vec3((5,0,0)).length_squared()
        25.0
        >>> vec3(1).length_squared()
        3.0
        _CPP_:
        return toPython(self->v[0]*self->v[0] + self->v[1]*self->v[1] + self->v[2]*self->v[2]);
        """
        return sum([x*x for x in self.v])

    def distance(self, arg3):
        """
        Returns the cartesian distance between self and other vector
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((5,0,0)).distance(vec3(0))
        5.0
        >>> vec3(1).distance(vec3(2)) == math.sqrt(3)
        True
        _CPP_:
        double v[self->len];
        if (!expectFromPythonSequence(arg1, v, self->len))
            return NULL;
        v[0] -= self->v[0];
        v[1] -= self->v[1];
        v[2] -= self->v[2];
        return toPython(std::sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]));
        """
        return math.sqrt(sum([(x-arg3[i])*(x-arg3[i]) for i, x in enumerate(self.v)]))

    def distance_squared(self, arg3):
        """
        Returns the square of the cartesian distance between self and other vector
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((5,0,0)).distance_squared(vec3(0))
        25.0
        >>> vec3(1).distance_squared(vec3(2))
        3.0
        _CPP_:
        double v[self->len];
        if (!expectFromPythonSequence(arg1, v, self->len))
            return NULL;
        v[0] -= self->v[0];
        v[1] -= self->v[1];
        v[2] -= self->v[2];
        return toPython(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
        """
        return sum([(x-arg3[i])*(x-arg3[i]) for i, x in enumerate(self.v)])

    def dot(self, arg3):
        """
        Returns the dot product of self and other vec3
        :param arg3: float sequence of length 3
        :return: float
        >>> vec3((1,2,3)).dot((4,5,6)) # (1*4)+(2*5)+(3*6)
        32.0
        _CPP_:
        double v[self->len];
        if (!expectFromPythonSequence(arg1, v, 3))
            return NULL;
        return toPython(self->v[0]*v[0] + self->v[1]*v[1] + self->v[2]*v[2]);
        """
        tools.check_float_sequence(arg3, len(self))
        return sum([x * float(arg3[i]) for i, x in enumerate(self.v)])


    # ------ inplace methods -------

    def floor(self):
        """
        Applies the floor() function to all elements, INPLACE
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).floor()
        vec3(0, 1, 2)
        >>> vec3((-1.1, -1.9, -0.9)).floor()
        vec3(-2, -2, -1)
        _CPP_:
        return vectorUnaryOpInplace(self, [](double v){ return std::floor(v); });
        """
        self.v = [math.floor(x) for x in self.v]
        return self

    def round(self):
        """
        Applies floor(+.5) to all elements, INPLACE
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).round()
        vec3(0, 2, 3)
        >>> vec3((-1.1, -1.9, -0.9)).round()
        vec3(-1, -2, -1)
        _CPP_:
        """
        self.v = [math.floor(x+.5) for x in self.v]
        return self

    def normalize(self):
        """
        Normalizes the vector, e.g. makes it length 1, INPLACE
        :return: self
        >>> vec3((1,1,0)).normalize()
        vec3(0.707107, 0.707107, 0)
        >>> vec3((1,2,3)).normalize().length() == 1
        True
        """
        l = self.length()
        self.v = [x / l for x in self.v]
        return self

    def normalize_safe(self):
        """
        Normalizes the vector, e.g. makes it length 1, INPLACE
        If the length is zero, this call does nothing
        :return: self
        >>> vec3((1,1,0)).normalize_safe()
        vec3(0.707107, 0.707107, 0)
        >>> vec3(0).normalize_safe()
        vec3(0, 0, 0)
        """
        l = self.length()
        if not l == 0.:
            self.v = [x / l for x in self.v]
        return self

    def cross(self, arg3):
        """
        Makes this vector the cross-product of this and arg3, INPLACE
        The cross product is always perpendicular to the plane described by the two vectors
        :param arg3: float sequence of length 3
        :return: self
        >>> vec3((1,0,0)).cross((0,1,0))
        vec3(0, 0, 1)
        >>> vec3((1,0,0)).cross((0,0,1))
        vec3(0, -1, 0)
        >>> vec3((0,1,0)).cross((0,0,1))
        vec3(1, 0, 0)
        _CPP_:
        double v[self->len];
        if (!expectFromPythonSequence(arg1, v, self->len))
            return NULL;
        double   x = self->v[1] * v[2] - self->v[2] * v[1],
                 y = self->v[2] * v[0] - self->v[0] * v[2];
        self->v[2] = self->v[0] * v[1] - self->v[1] * v[0];
        self->v[1] = y;
        self->v[0] = x;
        Py_RETURN_SELF;
        """
        tools.check_float_sequence(arg3)
        x = self.y * arg3[2] - self.z * arg3[1]
        y = self.z * arg3[0] - self.x * arg3[2]
        self.z = self.x * arg3[1] - self.y * arg3[0]
        self.x = x
        self.y = y
        return self

    def reflect(self, norm):
        """
        Reflects this vector on a plane with given normal, INPLACE
        :param norm: float sequence of length 3
        :return: self
        Example: suppose ray coming from top-left, going down on a flat plane
        >>> vec3((2,-1,0)).reflect((0,1,0)).round()
        vec3(2, 1, 0)
        """
        tools.check_float_sequence(norm, 3)
        self.set(self - vec3(norm) * self.dot(norm) * 2.)
        return self

    def rotate_x(self, degree):
        """
        Rotates this vector around the x-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_x(90).round()
        vec3(1, -3, 2)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        y = self.y * ca - self.z * sa
        self.z = self.y * sa + self.z * ca
        self.y = y
        return self

    def rotate_y(self, degree):
        """
        Rotates this vector around the y-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_y(90).round()
        vec3(3, 2, -1)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca + self.z * sa
        self.z = -self.x * sa + self.z * ca
        self.x = x
        return self

    def rotate_z(self, degree):
        """
        Rotates this vector around the z-axis, INPLACE
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_z(90).round()
        vec3(-2, 1, 3)
        """
        degree *= const.DEG_TO_TWO_PI
        sa = math.sin(degree)
        ca = math.cos(degree)
        x = self.x * ca - self.y * sa
        self.y = self.x * sa + self.y * ca
        self.x = x
        return self

    def rotate_axis(self, axis, degree):
        """
        Rotates this vector around an arbitrary axis, INPLACE
        :param axis: float sequence of length 3
        :param degree: the degrees [0., 360.]
        :return: self
        >>> vec3((1,2,3)).rotate_axis((1,0,0), 90) == vec3((1,2,3)).rotate_x(90)
        True
        """
        tools.check_float_sequence(axis, 3)
        degree *= const.DEG_TO_TWO_PI
        si = math.sin(degree)
        co = math.cos(degree)

        m = axis[0] * axis[0]+ axis[1] * axis[1] + axis[2] * axis[2]
        ms = math.sqrt(m)

        x = (axis[0] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.x * (axis[1] * axis[1] + axis[2] * axis[2]) + axis[0] * (-axis[1] * self.y - axis[2] * self.z))
            + si * ms * (-axis[2] * self.y + axis[1] * self.z)) / m
        y = (axis[1] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.y * (axis[0] * axis[0] + axis[2] * axis[2]) + axis[1] * (-axis[0] * self.x - axis[2] * self.z))
            + si * ms * (axis[2] * self.x - axis[0] * self.z)) / m
        self.z = (axis[2] * (axis[0] * self.x + axis[1] * self.y + axis[2] * self.z)
            + co * (self.z * (axis[0] * axis[0] + axis[1] * axis[1]) + axis[2] * (-axis[0] * self.x - axis[1] * self.y))
            + si * ms * (-axis[1] * self.x + axis[0] * self.y)) / m
        self.x = x
        self.y = y
        return self

    # --- value-copying methods ---

    def floored(self):
        """
        Returns a vector with the floor() function applied to all elements
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).floored()
        vec3(0, 1, 2)
        >>> vec3((-1.1, -1.9, -0.9)).floored()
        vec3(-2, -2, -1)
        """
        return vec3(self.v).floor()

    def rounded(self):
        """
        Returns a vector with floor(+.5) applied to all elements
        :return: self
        >>> vec3((0.1, 1.5, 2.9)).rounded()
        vec3(0, 2, 3)
        >>> vec3((-1.1, -1.9, -0.9)).rounded()
        vec3(-1, -2, -1)
        """
        return vec3(self.v).round()

    def normalized(self):
        """
        Returns normalized vector, e.g. makes it length 1.
        :return: self
        >>> vec3((1,1,0)).normalized()
        vec3(0.707107, 0.707107, 0)
        >>> vec3((1,2,3)).normalized().length() == 1
        True
        """
        return vec3(self.v).normalize()

    def normalized_safe(self):
        """
        Returns normalized vector, e.g. makes it length 1.
        Does nothing if length is 0.
        :return: self
        >>> vec3((1,1,0)).normalized_safe()
        vec3(0.707107, 0.707107, 0)
        >>> vec3(0).normalized_safe()
        vec3(0, 0, 0)
        """
        return vec3(self.v).normalize_safe()

    def crossed(self, arg3):
        """
        Returns the cross-product of this vector and arg3
        The cross product is always perpendicular to the plane described by the two vectors
        :param arg3: float sequence of length 3
        :return: self
        >>> vec3((1,0,0)).crossed((0,1,0))
        vec3(0, 0, 1)
        >>> vec3((1,0,0)).crossed((0,0,1))
        vec3(0, -1, 0)
        >>> vec3((0,1,0)).crossed((0,0,1))
        vec3(1, 0, 0)
        """
        return vec3(self.v).cross(arg3)

    def reflected(self, norm):
        """
        Returns the this vector reflected on a plane with given normal
        :param norm: float sequence of length 3
        :return: self
        Example: suppose ray coming from top-left, going down on a flat plane
        >>> vec3((2,-1,0)).reflected((0,1,0)).rounded()
        vec3(2, 1, 0)
        """
        return vec3(self.v).reflect(norm)

    def rotated_x(self, degree):
        """
        Returns this vector rotated around the x-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_x(90).rounded()
        vec3(1, -3, 2)
        """
        return vec3(self).rotate_x(degree)

    def rotated_y(self, degree):
        """
        Returns this vector rotated around the y-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_y(90).rounded()
        vec3(3, 2, -1)
        """
        return vec3(self).rotate_y(degree)

    def rotated_z(self, degree):
        """
        Returns this vector rotated around the z-axis
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_z(90).rounded()
        vec3(-2, 1, 3)
        """
        return vec3(self).rotate_z(degree)

    def rotated_axis(self, axis, degree):
        """
        Returns this vector rotated around an arbitrary axis
        :param axis: float sequence of length 3
        :param degree: the degrees [0., 360.]
        :return: vec3
        >>> vec3((1,2,3)).rotated_axis((1,0,0), 90) == vec3((1,2,3)).rotated_x(90)
        True
        """
        return vec3(self).rotate_axis(axis, degree)

if __name__ == "__main__":
    import doctest
    doctest.testmod()