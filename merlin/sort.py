from .common import Builder

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
        return Asc(field)

    @staticmethod
    def desc(field):
        return Desc(field)

