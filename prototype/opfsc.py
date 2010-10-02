import syslog
from urllib import urlopen
import stat


def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)


class OPFSClient:
    def __init__(self, target):
        self.target = target

    def read(self, path, size, offset):
        param = {
            'mode': 'read',
            'size': str(size),
            'offset': str(offset)
            }
        path = self._build_url(path, param)

        return self.request('GET', path)

    def readdir(self, path):
        path = self._build_url(path, {'mode': 'readdir'})
        ret = self.request('GET', path)
        if ret != "":
            return ret
        else:
            return None

    def stat(self, path):
        path = self._build_url(path, {'mode': 'stat'})
        ret = self.request('GET', path)
        if ret != "":
            return ret
        else:
            return None

    def request(self, method, path):
        return urlopen('http://' + self.target + path).read()

    def _build_url(self, url, param):
        return url + '?' + '&'.join(
            map(lambda key: key + '=' + param[key],
                param.keys()))
