import os
import stat
import errno
import syslog
import sys
from urllib2 import quote
from opfsc import OPFSClient
from opfsutil import OPFSUtil, OPFSStat
import syslog

try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse

read_cache = {}
stat_cache = {}

if not hasattr(fuse, '__version__'):
    raise RuntimeError(
        "your fuse-py doesn't know of fuse. \
__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)


class OPFSMounter(Fuse):
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        self.peers_file = '~/.opfs_peers'
        self.peer_client_map = {}
        self.debug = False

    """
    Fuse required methods
    """
    def getattr(self, path):
        self._log("getattr: %s" % (path))
        ret = -errno.ENOENT

        try:
            # get attribute from all peers
            for peer in self.peers:
                ret = self._opfs_stat(path, peer)
                if ret != -errno.ENOENT:
                    break

        except Exception, info:
            self._log("getattr error: %s" % (info))

        return ret

    def readdir(self, path, offset):
        self._log("readdir: %s" % (path))
        try:
            dirs = ['.', '..']

            # get direntry from all peers
            for peer in self.peers:
                resp = self._opfs_readdir(path, peer)
                if not resp:
                    self._log("%s's response is invalid" % (peer))
                    continue
                for dirname in resp.split('\n'):
                    if not(dirname in dirs):
                        dirs.append(dirname)

        except Exception, info:
            self._log("readdir error: %s" % (info))

        for r in dirs:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        self._log("open: %s" % (path))
        # open supports READONLY access
        try:
            peer = self._search_peer_by_path(path)
            if peer:
                if self._is_readonly_flag(flags):
                    # ok
                    global stat_cache
                    stat_cache[path] = self._opfs_stat(path, peer)
                    return
                else:
                    # write not support
                    return -errno.EACCES
            else:
                return -errno.ENOENT

        except Exception, info:
            self._log("open error: %s" % (info))

    def read(self, path, size, offset):
        global read_cache
        self._log("read: %s ,size=%d, offset=%d" % (path, size, offset))
        if path in read_cache:
            if read_cache[path][0] == offset:
                if len(read_cache[path][1]) == size:
                    return read_cache[path][1]
        try:
            peer = self._search_peer_by_path(path)

            filesize = self._opfs_filesize(path, peer)
            if filesize:
                if offset + (size * 2) < filesize:
                    # caching read
                    data = self._opfs_read(path, size * 2, offset, peer)
                    ret = data[0:len(data) / 2]
                    read_cache[path] = [offset + size, data[len(data) / 2:]]
                    return ret
                if offset < filesize:
                    # normal read
                    return self._opfs_read(path, size, offset, peer)
                else:
                    # invalid offset
                    return ''
            return -errno.ENOENT

        except Exception, info:
            self._log("read error: %s" % (info))

    """
    public methods
    """
    def setup_peer(self):
        self.peers_file = os.path.realpath(os.path.expanduser(self.peers_file))
        self._log("config file: %s" % (self.peers_file))
        if os.path.exists(self.peers_file):
            candidates = OPFSUtil.read_peers_file(self.peers_file)
            self.peers = []
            for peer in candidates:
                if self._get_opfs_client(peer).is_alive():
                    self.peers.append(peer)

            if len(self.peers) == 0:
                print "please setup %s" % (self.peers_file)
                sys.exit(-1)

        else:
            OPFSUtil.create_peers_file(self.peers_file)
            print "please setup %s" % (self.peers_file)
            sys.exit(-1)

    """
    internal methods
    """
    def _log(self, message):
        if self.debug:
            syslog.openlog("OPFS")
            syslog.syslog(syslog.LOG_ALERT, message)

    def _get_opfs_client(self, peer):
        ret = None
        if peer in self.peer_client_map:
            ret = self.peer_client_map[peer]
        else:
            ret = OPFSClient(peer)
            self.peer_client_map[peer] = ret
        return ret

    def _is_readonly_flag(self, flags):
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        return (flags & accmode) == os.O_RDONLY

    def _opfs_readdir(self, path, peer):
        path = path
        try:
            return self._get_opfs_client(peer).readdir(path)
        except Exception, info:
            self._log("_opfs_readdir: %s" % (info))
            return None

    def _opfs_read(self, path, size, offset, peer):
        path = path
        return self._get_opfs_client(peer).read(path, size, offset)

    def _opfs_stat(self, path, peer):
        path = path
        try:
            stat_info = self._get_opfs_client(peer).stat(path)
            if stat_info:
                return OPFSStat(stat_info)
            else:
                return None
        except Exception, info:
            self._log("_opfs_stat: %s" % (info))
            return None

    def _opfs_filesize(self, path, peer):
        global stat_cache
        st = None
        if not (path in stat_cache):
            stat_cache[path] = self._opfs_stat(path, peer)

        st = stat_cache[path]
        if st:
            return st.st_size
        else:
            return None

    def _search_peer_by_path(self, path):
        for peer in self.peers:
            st = self._opfs_stat(path, peer)
            if st:
                return peer


def main():
    usage = """
OnePiece FS

""" + Fuse.fusage
    mounter = OPFSMounter(version="%prog " + fuse.__version__,
                  usage=usage,
                  dash_s_do='setsingle')
    mounter.parser.add_option(mountopt="peers", metavar="filename", default='',
                             help="peer address and port")
    mounter.parser.add_option(mountopt="debug", metavar="", default='False',
                             help="debug mode")

    mounter.parse(values=mounter, errex=1)
    mounter.setup_peer()

    mounter.main()

if __name__ == '__main__':
    main()
