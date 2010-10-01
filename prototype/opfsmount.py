import os, stat, errno
import syslog
from opfsc import OPFSClient
import syslog

try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

def log(message):
    syslog.openlog("OPFS")
    syslog.syslog(syslog.LOG_ALERT, message)


class OPFS(Fuse):

    #def __init__(self, memcache, *args, **kw):
    #fuse.Fuse.__init__(self, *args, **kw)
        ##self.__memcache = memcache

    def getattr(self, path):
        try:
            ret = OPFSClient().PROPFIND(path)
        except Exception, info:
            log("getattr error: %s" % (info))

        if ret:
            return ret
        else:
            return -errno.ENOENT

    def readdir(self, path, offset):
        try:
            resp = OPFSClient().GET(path)
            dirs = resp.split('\n')
            dirs.append('.')
            dirs.append('..')

            for r in dirs:
                yield fuse.Direntry(r)
        except Exception, info:
            log("readdir error: %s" % (info))

    def open(self, path, flags):
        try:
            ret = OPFSClient().PROPFIND(path)
        except Exception, info:
            log("open error: %s" % (info))

        if ret:
            accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
            if (flags & accmode) != os.O_RDONLY:
                return -errno.EACCES
            else:
                return
        else:
            return -errno.ENOENT

    def read(self, path, size, offset):
        try:
            filesize = self._file_size(path)
            if filesize != None:
                if offset < filesize:
                    return OPFSClient().GET(path, size, offset)
                else:
                    return ''

        except Exception, info:
            log("read error: %s" % (info))

        return -errno.ENOENT

    def _stat(self, path):
        return OPFSClient().PROPFIND(path)

    def _file_size(self, path):
        st = self._stat(path)
        if st:
            return st.st_size
        else:
            return None

def main():
    usage="""
Userspace hello example

""" + Fuse.fusage
    server = OPFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')
    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
