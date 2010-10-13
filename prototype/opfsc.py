import syslog
import socket
default_timeout = 5
socket.setdefaulttimeout(default_timeout)
import urllib2
import stat
from urlgrabber.keepalive import HTTPHandler


def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)


class OPFSClient:
    def __init__(self, target):
        self.target = target
        self.keepalive_handler = HTTPHandler()
        self.opener = urllib2.build_opener(self.keepalive_handler)
        urllib2.install_opener(self.opener)

    def urlopen(self, url):
        return urllib2.urlopen(url)
        
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

        return self.request('GET', path, param)

    def readdir(self, path):
        ret = self.request('GET', path, {'mode': 'readdir'})
        if ret != "":
            return ret
        else:
            return None

    def stat(self, path):
        ret = self.request('GET', path, {'mode': 'stat'})
        if ret != "":
            return ret
        else:
            return None

    def request(self, method, path, param):
        path = self._build_url(urllib2.quote(path), param)
        return self.urlopen('http://' + self.target + path).read()

    def _build_url(self, url, param):
        return url + '?' + '&'.join(
            map(lambda key: key + '=' + param[key],
                param.keys()))
