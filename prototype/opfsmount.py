import os
import stat
import errno
import re
import syslog
import sys
from opfsc import OPFSClient
import syslog

try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError(
        "your fuse-py doesn't know of fuse. \
__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)


class OPFS(Fuse):

    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.peers_file = '~/.opfs_peers'
        self.debug = False

    def log(self, message):
        if self.debug:
            syslog.openlog("OPFS")
            syslog.syslog(syslog.LOG_ALERT, message)

    def getattr(self, path):
        try:
            ret = None

            # get attribute from all peers
            for peer in self.peers:
                ret = self._stat_opfs(path, peer)
                if ret:
                    break

            if ret:
                return ret
            else:
                return -errno.ENOENT

        except Exception, info:
            self.log("getattr error: %s" % (info))

    def readdir(self, path, offset):
        try:
            dirs = ['.', '..']

            # get direntry from all peers
            for peer in self.peers:
                resp = self._readdir_opfs(path, peer)
                for dirname in resp.split('\n'):
                    if not(dirname in dirs):
                        dirs.append(dirname)

            for r in dirs:
                yield fuse.Direntry(r)

        except Exception, info:
            self.log("readdir error: %s" % (info))

    def open(self, path, flags):
        # open supports READONLY access
        try:
            if self._search_peer_by_path(path):
                if self._is_readonly(flags):
                    # ok
                    return
                else:
                    # write not support
                    return -errno.EACCES
            else:
                return -errno.ENOENT

        except Exception, info:
            self.log("open error: %s" % (info))

    def read(self, path, size, offset):
        try:
            peer = self._search_peer_by_path(path)

            filesize = self._file_size_opfs(path, peer)
            if filesize:
                if offset < filesize:
                    return self._read_opfs(path, size, offset, peer)
                else:
                    # invalid offset
                    return ''
            return -errno.ENOENT

        except Exception, info:
            self.log("read error: %s" % (info))

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
        f.write("#please write 1 entry 1 file (ex. localhost:5656)\n")
        f.close

    def read_peers_file(self):
        # '#' line is comment
        regex = re.compile("\s*[^#]\S+")
        f = open(self.peers_file, 'r')
        data = f.read()
        peers = []
        for l in data.split("\n"):
            if regex.match(l):
                peers.append(l)
        return peers

    def _is_readonly(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        return (flags & accmode) == os.O_RDONLY

    def _readdir_opfs(self, path, peer):
        return OPFSClient(peer).GET(path)

    def _read_opfs(self, path, size, offset, peer):
        return OPFSClient(peer).GET(path, size, offset)

    def _stat_opfs(self, path, peer):
        return OPFSClient(peer).PROPFIND(path)

    def _file_size_opfs(self, path, peer):
        st = self._stat_opfs(path, peer)
        if st:
            return st.st_size
        else:
            return None

    def _search_peer_by_path(self, path):
        for peer in self.peers:
            st = self._stat_opfs(path, peer)
            if st:
                return peer


def main():
    usage = """
OnePiece FS

""" + Fuse.fusage
    server = OPFS(version="%prog " + fuse.__version__,
                  usage=usage,
                  dash_s_do='setsingle')
    server.parser.add_option(mountopt="peers", metavar="filename", default='',
                             help="peer address and port")
    server.parser.add_option(mountopt="debug", metavar="", default='False',
                             help="debug mode")

    server.parse(values=server, errex=1)
    server.setup_peer()

    server.main()

if __name__ == '__main__':
    main()
