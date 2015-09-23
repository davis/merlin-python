from collections import Iterable
import re

from common import Builder
from error import ValidationError

class Formatter(object):
    def __call__(self, v):
        raise NotImplementedError()

    def andThen(self, f2):
        return AndThenF(self, f2)

    def __rshift__(self, next):
        return self.andThen(next)

    def __lshift__(self, next):
        return next.andThen(self)

class AndThenF(Formatter):
    def __init__(self, f1, f2):
        self.f1 = f1
        self.f2 = f2

    def __call__(self, v):
        return self.f2(self.f1(v))

class _IdentityF(Formatter):
    def __call__(self, v):
        return v

IdentityF = _IdentityF()

class DelimF(Formatter):
    def __init__(self, d):
        self.delim = d

    def __call__(self, vs):
        if not isinstance(vs, (list, tuple)):
            vs = [v]

        return self.delim.join(unicode(v) for v in vs)

class MapF(Formatter):
    def __init__(self, f):
        self.f = f

    def __call__(self, vs):
        return [self.f(v) for v in vs]

class ToListF(Formatter):
    def __call__(self, v):
        if not isinstance(v, list):
            v = [v]

        return v

class _BuildF(Formatter):
    def __call__(self, v):
        return v.build()

BuildF = _BuildF()

class Validator(object):
    def test(self, v):
        raise NotImplementedError()

    def validate(self, v):
        raise NotImplementedError()

    def __or__(self, next):
        return OrValidator(self, next)

    def __and__(self, next):
        return AndValidator(self, next)

class OrValidator(Validator):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def test(self, v):
        return self.v1.test(v) or self.v2.test(v)

    def validate(self, v):
        if not self.test(v):
            self.v1.validate(v)
            self.v2.validate(v)

        return True

class AndValidator(Validator):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def test(self, v):
        return self.v1.test(v) and self.v2.test(v)

    def validate(self, v):
        self.v1.validate(v)
        self.v2.validate(v)
        return True

class LambdaValidator(Validator):
    def __init__(self, f, message):
        self.f = f
        self.message = message

    def test(self, v):
        return self.f(v)

    def validate(self, v):
        if not self.test(v):
            raise ValidationError('Field: %s - %s' % (v, self.message))

        return True

IntValidator = LambdaValidator(
        lambda v: isinstance(v, (int, long)), 
        "needs to be an int"
)

PosIntValidator = LambdaValidator(
        lambda v: IntValidator.test(v) and v >= 0,
        "needs to be a positive integer"
)

RegexValidator = lambda r: (lambda rx: LambdaValidator(
        lambda v: isinstance(v, int) or rx.match(v) is not None,
        "Field does not match the correct specification"
))(re.compile(r))

IdValidator = RegexValidator("^[a-z][a-z0-9_]{0,63}$")

IsValidator = lambda t: LambdaValidator(
        lambda v: isinstance(v, t),
        "needs to be of type `%s`" % t
)

BuilderValidator = IsValidator(Builder)

ListOfValidator = lambda t: LambdaValidator(
    lambda v: isinstance(v, list) and all(isinstance(x, t) for x in v),
    "needs to be a list of type %s" % (t,)
)

ForAllValidator = lambda vd: LambdaValidator(
    lambda xs: isinstance(xs, Iterable) and all(vd.test(x) for x in xs),
    "failed validation for %s" % (vd,)
)

class FieldType(Validator, Formatter):
    def __init__(self, validator, formatter):
        self.validator = validator
        self.formatter = formatter

    def test(self, v):
        return self.validator.test(v)

    def validate(self, v):
        return self.validator.validate(v)

    def format(self, v):
        return self(v)

    def __call__(self, v):
        return self.formatter(v)
