from collections import OrderedDict
from .common import Builder

class Facet(Builder):
    def __init__(self, ftype, field, key=None): 
        self.ftype = ftype
        self.field = field 
        self.key = key

    def _build(self, extras=None):
        params = OrderedDict()
        params['field'] = self.field
        params['type'] = self.ftype
        if self.key is not None:
            params['key'] = self.key

        if extras is not None:
            params.update(extras)

        return '/'.join('%s=%s' % (k, v) for k, v in params.iteritems())

    def build(self):
        return self._build()

    @staticmethod
    def enum(*args, **kwargs):
        return EnumFacet(*args, **kwargs)

    @staticmethod
    def hist(*args, **kwargs):
        return HistFacet(*args, **kwargs)

    @staticmethod
    def range(*args, **kwargs):
        return RangeFacet(*args, **kwargs)

class EnumFacet(Facet):
    def __init__(self, field, num=15, key=None, exclude=None):
        super(EnumFacet, self).__init__('enum', field, key)
        self.num = num
        self.exclude = () if exclude is None else tuple(exclude)

    def build(self):
        ps = OrderedDict(num=self.num)
        if self.exclude:
            ps['ex'] = ','.join(self.exclude)

        return self._build(ps)

class HistFacet(Facet):
    def __init__(self, field, start, end, gap, key=None):
        assert all(isinstance(s, (int, long)) for s in (start, end, gap))
        super(HistFacet, self).__init__('hist', field, key)
        self.start = start
        self.end = end
        self.gap = gap

    def build(self):
        ps = OrderedDict(range='[%s:%s:%s]' % (self.start, self.end, self.gap))
        return self._build(ps)

class RangeFacet(Facet):
    def __init__(self, field, key=None):
        super(RangeFacet, self).__init__('range', field, key)

