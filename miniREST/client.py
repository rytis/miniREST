import httplib


class RESTResource(object):
    def __init__(self):
        self.status = None
        self.reason = None
        self.raw_data = None


class RESTClient(object):
    """
    Simple interface to the REST web services. Supports 'GET', 'PUT', 'POST' and 'DELETE' methods.
    Tailored towards JSON based services, although should be pretty straightforward to implement
    different data payload methods:
        - subclass from RESTClient
        - implement _build_<data type>_payload method (see json example)
        - pass data to get, put, etc method as 'data_<data type>' keyword argument

    Examples:

        c = RESTClient('api.example.com')
        c.get('/api/v1/resource/')
        c.put('/api/v1/resource/instance1/', data_json={'params': ['res1a', 'res1b']})
        c.post('/api/v1/resource/', data_json={'name': 'instance2', 'params': ['res2a', 'res2b']})
        c.delete('/api/v1/resource/instance1/')
    """

    def __init__(self, url):
        self._method = None
        self._url = url
        if self._url.endswith('/'):
            self._url = self._url[:-1]
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json'}

    def _build_json_payload(self, data):
        try:
            import json
        except ImportError:
            raise RuntimeError('json not installed')
        return json.dumps(data)

    def _rest_call(self, resource=None, **kwargs):
        http_body = None
        if kwargs:
            for key in kwargs:
                if key.startswith('data_'):
                    http_body = getattr(self, "_build_%s_payload" % key[5:])(kwargs[key])
        c = httplib.HTTPConnection(self._url)
        c.request(self._method, resource, body=http_body, headers=self.headers)
        resp = c.getresponse()
        rest_obj = RESTResource()
        rest_obj.status = resp.status
        rest_obj.reason = resp.reason
        rest_obj.raw_data = resp.read()
        c.close()
        return rest_obj

    def __getattr__(self, item):
        if item not in ('get', 'put', 'post', 'delete'):
            raise AttributeError("Method '%s' not implemented" % item)
        self._method = item
        return self._rest_call
