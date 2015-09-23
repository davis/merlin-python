import json
from urllib import urlencode
from urlparse import urljoin
from collections import OrderedDict

from .error import MerlinException
from .common import Builder, Api
from .utils import *
from .filter import NF
from .search import Hits

OneOrNValidator = lambda v: ForAllValidator(v) | v
class Vrec(Api):
    PREFIX = "vrec"
    FIELD_TYPES = {
        "id": FieldType(IdValidator, IdentityF),
        "num":   FieldType(PosIntValidator, IdentityF),
        "fields": FieldType(
            ForAllValidator(IsValidator(basestring)),
            DelimF(",")
        ),
        "filter": FieldType(
            OneOrNValidator(IsValidator(NF)),
            ToListF() >> MapF(BuildF)
        )
    }

    def __init__(self, id, num=None, filter=None, fields=None):
        self.id = id
        self.num = num
        self.filter = filter
        self.fields = fields

    def build(self):
        params = OrderedDict(id=self.id)

        # Sigh
        for k in ('fields', 'filter', 'num'):
            v = getattr(self, k)
            if v is not None:
                ft = self.FIELD_TYPES.get(k)
                if ft is not None:
                    ft.validate(v)
                    v = ft.format(v)

                params[k] = v

        return urljoin(self.PREFIX, "?%s" % urlencode(params, True))

    def process_results(self, raw):
        return VrecResults.parse(raw)
        
class VrecResults(object):

    def __init__(self, doc, qid, num, hits, raw):
        self.raw = raw
        self.doc = doc
        self.qid = qid
        self.num = num
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
        doc = results['doc']
        hits = Hits(results['numfound'], results['hits'])
        return cls(doc, data['qid'], data['num'], hits, data)

    def __unicode__(self):
        return u"Vrec(id='%s', numFound=%s)" % \
                (self.doc.get('id'), self.hits.numFound)

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


