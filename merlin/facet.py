
class Facet(object):
    def __init__(self, field, key):
        self.field = field 
        self.key = key

class EnumFacet(Facet):
    def __init__(self, field, num, key=None, exclude=None):
        assert isinstance(num, int)
        super(EnumFacet, self).__init__(field, key)
        self.num = num
        self.exclude = () if exclude is None else tuple(exclude)

class HistFacet(Facet):
    def __init__(self, field, start, end, gap, key=None):
        assert all(isinstance(s, (int, long)) for s in (start, end, gap))
        super(HistFacet, self).__init__(field, key)
        self.start = start
        self.end = end
        self.gap = gap

