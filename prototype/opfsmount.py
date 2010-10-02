import os, stat, errno, re
import syslog, sys
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

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.peers_file = '~/.opfs_peers'

    def getattr(self, path):
        ret = None
        try:
            for peer in self.peers:
                log(peer)
                ret = OPFSClient(peer).PROPFIND(path)
                if ret:
                    break
        except Exception, info:
            log("getattr error: %s" % (info))

        if ret:
            return ret
        else:
            return -errno.ENOENT

    def readdir(self, path, offset):
        dirs = ['.', '..']
        try:
            for peer in self.peers:
                resp = OPFSClient(peer).GET(path)
                for dirname in resp.split('\n'):
                    dirs.append(dirname)

            for r in dirs:
                yield fuse.Direntry(r)
        except Exception, info:
            log("readdir error: %s" % (info))

    def open(self, path, flags):
        try:
            for peer in self.peers:
                ret = OPFSClient(peer).PROPFIND(path)
                if ret != None:
                    break
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
            peer = None
            for candidate in self.peers:
                ret = OPFSClient(candidate).PROPFIND(path)
                if ret != None:
                    peer = candidate

            filesize = self._file_size(path, peer)
            if filesize != None:
                if offset < filesize:
                    return OPFSClient(peer).GET(path, size, offset)
                else:
                    return ''

        except Exception, info:
            log("read error: %s" % (info))

        return -errno.ENOENT

    def setup_peer(self):
        self.peers_file = os.path.realpath(os.path.expanduser(self.peers_file))
        print self.peers_file
        if os.path.exists(self.peers_file):
            self.peers = self.read_peers_file()
            if len(self.peers) == 0:
                print "please setup %s" % (self.peers_file)
                sys.exit(-1)

        else:
            self.create_peers_file()
            print "please setup %s" % (self.peers_file)
            sys.exit(-1)
        
    def create_peers_file(self):
        f = open(self.peers_file, 'w')
        f.write("#please write 1 entry 1 file\n#localhost:8000\n")
        f.close

    def read_peers_file(self):
        f = open(self.peers_file, 'r')
        data =f.read()
        peers = []
        for l in data.split("\n"):
            if re.compile("\s*[^#]\S+").match(l):
                peers.append(l)
        return peers
        
        
    def _stat(self, path, peer):
        return OPFSClient(peer).PROPFIND(path)

    def _file_size(self, path, peer):
        st = self._stat(path, peer)
        if st:
            return st.st_size
        else:
            return None

def main():
    usage="""
OnePiece FS

""" + Fuse.fusage
    server = OPFS(version="%prog " + fuse.__version__,
                  usage=usage,
                  dash_s_do='setsingle')
    server.parser.add_option(mountopt="peers", metavar="filename", default='',
                             help="peer address and port")

    server.parse(values=server, errex=1)
    server.setup_peer()

    server.main()

if __name__ == '__main__':
    main()
