from .common import Builder

class Group(Builder):
    def __init__(self, field, sort=None, num=None):
        self.field = field
        self.sort = sort
        self.num = num

    def build(self):
        res = ['field=%s' % self.field]
        if self.sort is not None:
            res.append('sort=%s' % self.sort.build())

        if self.num is not None:
            res.append('num=%s' % self.num)

        return '/'.join(res)
