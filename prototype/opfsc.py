import syslog
from httplib import HTTPConnection
import pickle
import stat

def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)

class OPFSClient:
    def GET(self, path, size = None, offset = None):
        if size != None and offset != None:
            path = path + '?size=' + str(size) + '&offset=' + str(offset)

        return self.request('GET', path)

    def PROPFIND(self, path):
        ret = self.request('PROPFIND', path)
        if ret != "":
            return pickle.loads(ret)
        else:
            return None

    def request(self, method, path):
        conn = HTTPConnection("localhost", 8000)
        conn.request(method, path)
        resp = conn.getresponse()
        return resp.read()

#a = OPFSClient()
#print a.GET("/virtualenv-1.5.1/virtualenv.py")
#st = a.PROPFIND("/tmp")
#print st.st_mode
