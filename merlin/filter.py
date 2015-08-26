class Filter(object):
    """
    Standard search feature
    """
    __slots__ = ('field', 'op', 'value')
    def __init__(self, field, op, value):
        self.field = field
        self.op = op
        self.value = value

