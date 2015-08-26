from urlparse import ParseResult, urlunparse
__version__ = '0.0.1'

from .common import Api, Engine, DefaultEngine

# Standard defaults
HOSTS = {
    "prod":   "search-prod.search.blackbird.am",
    "stage": "search-dev.search.blackbird.am",
    "dev":    "search-dev.search.blackbird.am"
}

class Merlin(object):

    def __init__(self, company, environment, instance, 
            host=None, use_ssl=False, engine=DefaultEngine):

        self.company = company
        self.environment = environment
        self.instance = instance
        self.host = host if host is not None else HOSTS[environment]
        self.use_ssl = use_ssl
        self.engine = engine

    def build_url(self):
        pr = ParseResult(
            'https' if self.use_ssl else 'http',
            self.host,
            '/%s/' % '.'.join((self.company, self.environment, self.instance)),
            None, None, None)

        return urlunparse(pr)

    def __call__(self, api):
        assert isinstance(api, Api), "Requires an API instance!"
        return self.engine(self, api)

class F2(object):
    __slots__ = ("f1", "f2")
    def __init__(self, f1, f2):
        assert all(isinstance(f, (F2, Filter)) for f in (f1, f2))

        self.f1 = f1
        self.f2 = f2

class And(F2):
    pass

class Or(F2):
    pass

