from .common import Builder
class Sorter(Builder):
    def __init__(self, sorts):
        self.sorts = sorts

    def asc(self, field):
        return Sorter(self.sorts + [Asc(field)])

    def desc(self, field):
        return Sorter(self.sorts + [Desc(field)])

    def build(self):
        return ','.join(s.build() for s in self.sorts)

class SortField(Builder):
    def __init__(self, field):
        self.field = field

class Asc(SortField):
    def build(self):
        return '%s:asc' % self.field

class Desc(SortField):
    def build(self):
        return '%s:desc' % self.field

class Sort(object):
    @staticmethod
    def asc(field):
        return Sorter([Asc(field)])

    @staticmethod
    def desc(field):
        return Sorter([Desc(field)])

