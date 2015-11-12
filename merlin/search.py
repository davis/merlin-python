import json
from urllib import urlencode
from collections import OrderedDict

from .error import MerlinException
from .common import Builder, PApi
from .utils import *
from .sort import SortField
from .filter import NF
from .geo import Geo
from .group import Group

OneOrNValidator = lambda v: ForAllValidator(v) | v
class Search(PApi):
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
        ),
        "group": FieldType(
            IsValidator(Group),
            BuildF
        ),
        "geo": FieldType(
            IsValidator(Geo),
            BuildF
        ),
        "correct": FieldType(
            BoolValidator,
            BoolF()
        )
    }


    FIELDS = ('q', 'filter', 'facet', 'start', 'num', 'sort', 'fields', 'group', 'geo', 'correct')
    REQUIRED = ('q',)

    def __init__(self, q="", start=None, num=None, filter=None, 
                       facets=None, sort=None, fields=None, correct=None,
                       group=None, geo=None, index="products"):
        self.q = q
        self.start = start
        self.num = num
        self.filter = filter
        self.facet = facets
        self.sort = sort
        self.fields = fields
        self.group = group
        self.geo = geo
        self.correct = correct
        self.index = index

    def process_results(self, raw):
        return SearchResults.parse(raw)
        
class SearchResults(object):

    def __init__(self, q, qid, num, start, hits, facets, cq, raw):
        self.raw = raw
        self.q = q
        self.qid = qid
        self.num = num
        self.start = start
        self.hits = hits
        self.facets = facets
        self.cq = cq

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
        cq = results.get('cq')
        return cls(data['q'], data['qid'], data['num'], 
                data['start'], hits, facets, cq, data)

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

