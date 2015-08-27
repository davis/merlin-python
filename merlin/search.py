import json
from urllib import urlencode
from urlparse import urljoin
from collections import OrderedDict

from .error import MerlinException
from .common import Builder, Api
from .utils import *
from .sort import Sorter

class Search(Api):
    PREFIX = "search"
    FIELD_TYPES = {
        "start": FieldType(PosIntValidator, IdentityF),
        "num":   FieldType(PosIntValidator, IdentityF),
        "facet": FieldType(
            ForAllValidator(BuilderValidator) | BuilderValidator,
            ToListF().andThen(MapF(BuildF))
        ),
        "sort": FieldType(IsValidator(Sorter), BuildF), 
    }

    def __init__(self, q="", start=None, num=None, filters=None, 
                       facets=None, sort=None):
        self.q = q
        self.start = start
        self.num = num
        self.filter = filters
        self.facet = facets
        self.sort = sort

    def build(self):
        params = OrderedDict(q=self.q)

        # Sigh
        for k in ('filter', 'facet', 'start', 'num', 'sort'):
            v = getattr(self, k)
            if v is not None:
                ft = self.FIELD_TYPES.get(k)
                if ft is not None:
                    ft.validate(v)
                    v = ft.format(v)

                params[k] = v

        return urljoin(self.PREFIX, "?%s" % urlencode(params, True))

    def process_results(self, raw):
        return SearchResults.parse(raw)
        
class SearchResults(object):

    def __init__(self, q, num, start, hits):
        self.q = q
        self.num = num
        self.start = start
        self.hits = hits

    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        return self.hits[key]

    def __len__(self):
        return len(self.hits)

    def __nonzero__(self):
        return len(self) > 0
    
    @classmethod
    def parse(cls, raw):
        try:
            data = json.loads(raw)
        except ValueError:
            raise MerlinException("Unable to read results!")

        results = data['results']
        hits = Hits(results['numfound'], results['hits'])
        return cls(data['q'], data['num'], data['start'], hits)

    def __unicode__(self):
        return u"SearchResults(q='%s', numFound=%s)" % (self.q, self.hits.numFound)

    __repr__ = __unicode__

class Hits(object):
    def __init__(self, numFound, hits):
        self.numFound = numFound
        self.hits = hits

    def __getitem__(self, key):
        return self.hits[key]

    def __iter__(self):
        return iter(self.hits)

    def __len__(self):
        return len(self.hits)
