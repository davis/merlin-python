from .common import Builder

class Geo(Builder):
    def __init__(self, field, pt, dist, miles=False):
        assert isinstance(field, basestring), "Field needs to be a string"
        assert field, "Field needs to be a non-empty string"
        assert isinstance(pt, tuple) and \
            all(isinstance(p, (int, float)) for p in pt), \
            "pt needs to be a tuple of numbers"
        assert isinstance(dist, (int, float)), "Dst needs to be a number"
        assert dist > 0, "Dst needs to be greater than zero"
        assert isinstance(miles, bool), "Miles needs to be a bool"
        self.field = field
        self.pt = pt
        self.miles = miles
        self.dist = dist * 1.60934 if miles else dist

    def build(self):
        res = [
            'field=%s' % self.field,
            'pt=(%f,%f)' % (self.pt[0], self.pt[1]),
            'd=%0.3f' % self.dist,
        ]

        return '/'.join(res)
