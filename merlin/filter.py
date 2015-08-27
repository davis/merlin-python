from .common import Builder

def assert_op(v, op):
    assert isinstance(v, (int, float)), "Can only use '%s' for numbers" % op

class Field(object):

    def __init__(self, field):
        assert isinstance(field, basestring), "Field needs to be a string"
        assert field, "Field needs to be a non-empty string"
        self.field = field

    def _new_op(self, op, v):
        return FilterSet(self.field, op, v)

    def __lt__(self, v):
        raise NotImplementedError("Fields only support '<='")

    def __gt__(self, v):
        raise NotImplementedError("Fields only support '>='")

    def __le__(self, v):
        assert_op(v, '<=')
        return self._new_op('<=', slice(None, v))

    def __ge__(self, v):
        assert_op(v, '>=')
        return self._new_op('>=', slice(v, None))

    def __eq__(self, v):
        return self._new_op('=', v)

    def __ne__(self, v):
        return self._new_op('!=', v)

    def between(self, start, stop):
        assert all(isinstance(s, (int, float)) for s in (start, stop)), \
                "Start and stop need to be numbers"

        return self._new_op('in', slice(start, stop))

class NF(Builder):
    @staticmethod
    def cnf(f):
        return CNF(f)

    @staticmethod
    def dnf(f):
        return DNF(f)
    
class CNF(NF):
    def __init__(self, fs):
        self.fs = fs

    def build(self):
        return "exp=%s/type=cnf" % self.fs.build()

class DNF(NF):
    def __init__(self, fs):
        self.fs = fs

    def build(self):
        return "exp=%s/type=dnf" % self.fs.build()

ESCAPE_SET = {
    ",":  r"\,",
    "!":  r"\!",
    "|":  r"\|",
    '\\': r"\\"
}

class FilterSet(Builder):
    """
    Standard search feature
    """
    __slots__ = ('field', 'op', 'value')
    def __init__(self, field, op, value):
        self.field = field
        self.op = op
        self.value = value

    def or_(self, f2):
        return self | f2

    def __or__(self, f2):
        assert isinstance(f2, (FilterSet, F2)), "Can only or with another FilterSet!"
        return Or(self, f2)

    def and_(self, f2):
        return self & f2

    def __and__(self, f2):
        assert isinstance(f2, (FilterSet, F2)), \
                "Can only and with another FilterSet!"
        return And(self, f2)

    def _escape(self, v):
        v = unicode(v)
        if v.isalpha() or v.isdigit():
            return v

        return ''.join(ESCAPE_SET.get(c, c) for c in v)

    def __unicode__(self):
        if self.op == '<=':
            value = self.value.stop
        elif self.op == '>=':
            value = self.value.start
        elif self.op == 'in':
            value = '[%s:%s]' % (self.value.start, self.value.stop)
        else:
            value = self.value 

        return u'(`%s` %s `%s`)' % (self.field, self.op, value)

    __repr__ = __unicode__

    def build(self):
        # Le sigh.  Wish Python had ADTs
        if self.op in ('<=', '>=', 'in'):
            if self.op == 'in':
                start, stop = self.value.start, self.value.stop
            elif self.op == '<=':
                start, stop = '', self.value.stop
            elif self.op == '>=':
                start, stop = self.value.start, ''

            return '%s:[%s:%s]' % (self.field, start, stop)

        value = self._escape(self.value)
        if self.op == '!=':
            return '%s:!%s' % (self.field, value)

        return '%s:%s' % (self.field, value)

class F2(Builder):
    __slots__ = ("f1", "f2")
    def __init__(self, f1, f2):
        assert all(isinstance(f, (F2, FilterSet)) for f in (f1, f2))

        self.f1 = f1
        self.f2 = f2

    def __and__(self, f2):
        assert isinstance(f2, (FilterSet, F2)), \
                "Can only `and` with another FilterSet!"
        return And(self, f2)

    def __or__(self, f2):
        assert isinstance(f2, (FilterSet, F2)), \
                "Can only `or` with another FilterSet!"
        return Or(self, f2)

class And(F2):
    def build(self):
        return '%s,%s' % (self.f1.build(), self.f2.build())

    def __unicode__(self):
        return u"%s & %s" % (self.f1, self.f2)

    __repr__ = __unicode__

class Or(F2):
    def build(self):
        return '%s|%s' % (self.f1.build(), self.f2.build())

    def __unicode__(self):
        return u"%s | %s" % (self.f1, self.f2)

    __repr__ = __unicode__

