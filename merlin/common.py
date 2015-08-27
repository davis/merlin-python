import gzip
import urllib2
import urlparse
from cStringIO import StringIO
from contextlib import closing

class Builder(object):

    def build(self):
        raise NotImplementedError()

class Api(Builder):

    def process_results(self, data):
        raise NotImplementedError()

class Engine(object):
    def run(self):
        raise NotImplementedError()

class DefaultEngine(Engine):
    def __init__(self, env, api, timeout=None):
        self.env = env
        self.api = api
        self.timeout = timeout

    def __enter__(self):
        url = urlparse.urljoin(self.env.build_url(), self.api.build())
        req = self.build_request(url)

        with closing(urllib2.urlopen(req, timeout=self.timeout)) as h:

            if h.info().get('Content-Encoding') == 'gzip':
                data = self.decode_gzip(h)
            else:
                data = h.read()

            if h.code != 200:
                raise IOError("Bad response: %s" % data)

            return self.api.process_results(data)

    def __exit__(self, *args, **kwargs):
        pass

    def build_request(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'py-merlin-client')
        req.add_header('Accept-encoding', 'gzip')
        return req

    def decode_gzip(self, h):
        f = gzip.GzipFile(fileobj=StringIO(h.read()))
        return f.read()
