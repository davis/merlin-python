from urlparse import ParseResult, urlunparse
__version__ = '0.0.1'

from .common import Api, Engine, DefaultEngine, UploadEngine
from .upload import IndexOp

class Environment(object):

    def __init__(self, company, environment, instance, 
            host=None, use_ssl=False, version='v1', 
            engine=DefaultEngine):

        self.company = company
        self.environment = environment
        self.instance = instance
        self.host = host
        self.use_ssl = use_ssl
        self.engine = engine
        self.version = version

    def __call__(self, op):
        raise NotImplementedError()

# Standard defaults
HOSTS = {
    "prod":  "search-prod.search.blackbird.am",
    "stage": "search-staging.search.blackbird.am",
    "dev":   "search-dev.search.blackbird.am"
}

class Merlin(Environment):

    def __init__(self, *args, **kwargs):

        super(Merlin, self).__init__(*args, **kwargs)
        if self.host is None:
            self.host = HOSTS[self.environment]

    def build_url(self):
        fqn = '.'.join((self.company, self.environment, self.instance))
        pr = ParseResult(
            'https' if self.use_ssl else 'http',
            self.host,
            '%s/%s/' % (self.version, fqn),
            None, None, None)

        return urlunparse(pr)

    def __call__(self, api):
        assert isinstance(api, Api), "Requires an API instance!"
        return self.engine(self, api)

UPLOAD_HOSTS = {
    "prod":  "upload-prod.search.blackbird.am",
    "stage": "upload-staging.search.blackbird.am",
    "dev":   "upload-dev.search.blackbird.am"
}
class Uploader(Environment):

    def __init__(self, company, environment, instance, 
            username, authtoken, host=None, use_ssl=True,
            engine=UploadEngine):

        super(Uploader, self).__init__(company, environment, instance,
                host, use_ssl=use_ssl, engine=engine)

        self.username = username
        self.authtoken = authtoken

        if self.host is None:
            self.host = UPLOAD_HOSTS[self.environment]

    def __call__(self, op):
        assert isinstance(op, IndexOp), "Requires an IndexOp instance!"
        return self.engine(self, op)

