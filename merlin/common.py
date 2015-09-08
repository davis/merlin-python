from collections import OrderedDict
import gzip
from urllib import urlencode
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
    
    def _decode(self, h):
        if h.info().get('Content-Encoding') == 'gzip':
            return self.decode_gzip(h)
        else:
            return h.read()

    def decode_gzip(self, h):
        f = gzip.GzipFile(fileobj=StringIO(h.read()))
        return f.read()

    def build_request(self, url, data=None):
        if data is not None:
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)

        req.add_header('User-Agent', 'py-merlin-client')
        req.add_header('Accept-encoding', 'gzip')
        return req

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

            data = self._decode(h)

            if h.code != 200:
                raise IOError("Bad response: %s" % data)

            return self.api.process_results(data)

    def __exit__(self, *args, **kwargs):
        pass

class UploadEngine(Engine):
    def __init__(self, env, op, timeout=None):
        self.env = env
        self.op = op
        self.timeout = timeout

    def _build_url(self):
        proto = 'https' if self.env.use_ssl else 'http'
        url = '%s://%s/%s' % (proto, self.env.host, self.op.endpoint)
        return '%s?%s' % (url, urlencode(self._build_params(), True))

    def _build_params(self):
        return OrderedDict([
            ("user", self.env.username),
            ("token", self.env.authtoken),
            ("company_id", self.env.company),
            ("env", self.env.environment),
            ("instance_name", self.env.instance)
        ])

    def __enter__(self):
        url  = self._build_url()
        req  = self.build_request(url, self.op.build_json())
        data = self._execute(req)
        return self.op.process_results(data)
        
    def _execute(self, req):
        try:
            with closing(urllib2.urlopen(req, timeout=self.timeout)) as h:
                return self._decode(h)
        except urllib2.HTTPError, e:
            return self._decode(e)

    def __exit__(self, *args, **kwargs):
        pass

