import json
from urllib import urlencode
from urlparse import urljoin
from collections import OrderedDict

from .error import MerlinException
from .common import Builder, Api
from .utils import *
from .sort import SortField
from .filter import NF

OneOrNValidator = lambda v: ForAllValidator(v) | v
class Search(Api):
    PREFIX = "search"
    FIELD_TYPES = {
        "start": FieldType(PosIntValidator, IdentityF),
        "num":   FieldType(PosIntValidator, IdentityF),
        "facet": FieldType(
            OneOrNValidator(BuilderValidator),
            ToListF() >> MapF(BuildF)
        ),
        "sort": FieldType(
            OneOrNValidator(IsValidator(SortField)),
            ToListF() >> MapF(BuildF) >> DelimF(',')
        ), 
        "fields": FieldType(
            ForAllValidator(IsValidator(basestring)),
            DelimF(",")
        ),
        "filter": FieldType(
            OneOrNValidator(IsValidator(NF)),
            ToListF() >> MapF(BuildF)
        )
    }

    def __init__(self, q="", start=None, num=None, filter=None, 
                       facets=None, sort=None, fields=None):
        self.q = q
        self.start = start
        self.num = num
        self.filter = filter
        self.facet = facets
        self.sort = sort
        self.fields = fields

    def build(self):
        params = OrderedDict(q=self.q)

        # Sigh
        for k in ('filter', 'facet', 'start', 'num', 'sort', 'fields'):
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

    def __init__(self, q, num, start, hits, facets):
        self.q = q
        self.num = num
        self.start = start
        self.hits = hits
        self.facets = facets

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
        facets = Facets(results['facets'])
        return cls(data['q'], data['num'], data['start'], hits, facets)

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

class Facets(object):
    def __init__(self, facets):
        self.enums = self._build_enums(facets['enums'])
        self.histograms = self._build_hists(facets['histograms'])
        self.ranges = self._build_ranges(facets['ranges'])

    def _build_enums(self, ens):
        enums = {}
        for fname, v in ens.iteritems():
            enums[fname] = m = {}
            for fs in v.get('enums', []):
                m[f['term']] = f['count']

        return enums

    def _build_ranges(self, rngs):
        ranges = {}
        for fname, m in rngs.iteritems():
            ranges[fname] = (m['min'], m['max'])

        return ranges

    def _build_hists(self, hsts):
        hists = {}
        for fname, v in hsts.iteritems():
            hists[fname] = m = {}
            for f in v.get('histograms', []):
                to_v, from_v, count = f['to'], f['from'], f['count']
                m[(from_v, to_v)] = count

        return hists

