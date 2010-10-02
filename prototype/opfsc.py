import syslog
from httplib import HTTPConnection
import pickle
import stat


def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)


class OPFSClient:
    def __init__(self, target):
        try:
            host, port = target.split(":")
            self.host = host
            self.port = int(port)

        except Exception, info:
            raise RuntimeError("OPFSClient parameter error: %s" % (info))

    def GET(self, path, size=None, offset=None):
        if size != None and offset != None:
            param = {
                'size': str(size),
                'offset': str(offset)
                }
            parh = self._build_url(path, param)
            path = path + '?size=' + str(size) + '&offset=' + str(offset)
        log("PATH")
        log(path)
        return self.request('GET', path)

    def PROPFIND(self, path):
        ret = self.request('PROPFIND', path)
        if ret != "":
            return pickle.loads(ret)
        else:
            return None

    def request(self, method, path):
        conn = HTTPConnection(self.host, self.port)
        conn.request(method, path)
        resp = conn.getresponse()
        return resp.read()

    def _build_url(self, url, param):
        ret = url
        return url + '?' + '&'.join(map(lambda key: key + '=' + param[key],
                               param.keys()))
