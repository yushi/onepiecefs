import syslog
import socket
default_timeout = 5
socket.setdefaulttimeout(default_timeout)
from urllib import urlopen
import stat


def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)


class OPFSClient:
    def __init__(self, target):
        self.target = target

    def is_alive(self):
        global default_timeout
        ret = False
        host, port = self.target.split(':')

        try:
            socket.setdefaulttimeout(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            ret = True
        except Exception:
            pass
        socket.setdefaulttimeout(default_timeout)
        return ret

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
