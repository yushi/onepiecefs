import re
import os
import socket
import stat

class OPFSStat():
    def __init__(self, stat_str):
        if stat_str != None:
            for prop in stat_str.split("\n"):
                key, val = prop.split(':')
                if key == 'st_mode':
                    self.st_mode = int(val)
                elif key == 'st_ino':
                    self.st_ino = int(val)
                elif key == 'st_dev':
                    self.st_dev = int(val)
                elif key == 'st_nlink':
                    self.st_nlink = int(val)
                elif key == 'st_uid':
                    self.st_uid = int(val)
                elif key == 'st_gid':
                    self.st_gid = int(val)
                elif key == 'st_size':
                    self.st_size = int(val)
                elif key == 'st_atime':
                    self.st_atime = float(val)
                elif key == 'st_mtime':
                    self.st_mtime = float(val)
                elif key == 'st_ctime':
                    self.st_ctime = float(val)


class OPFSUtil:
    @classmethod
    def create_peers_file(self, path):
        f = open(path, 'w')
        f.write("#please write 1 entry 1 file (ex. localhost:5656)\n")
        f.close

    @classmethod
    def read_peers_file(self, path):
        # '#' line is comment
        regex = re.compile("\s*[^#]\S+")
        f = open(path, 'r')
        data = f.read()
        peers = []
        for l in data.split("\n"):
            if regex.match(l):
                peers.append(l)
        return peers

    @classmethod
    def get_peer_addrs(self, path):
        addrs = ['127.0.0.1']
        if os.path.exists(path):
            peers = OPFSUtil.read_peers_file(path)
            for peer in peers:
                host, port = peer.split(":")
                for info in socket.getaddrinfo(host, port):
                    addr = info[4][0]
                    if not (addr in addrs):
                        addrs.append(addr)
        else:
            addrs = None

        return addrs

    @classmethod
    def stat2str(self,st):
        values = [
            ['st_mode', str(st.st_mode)],
            ['st_ino',  str(st.st_ino)],
            ['st_dev', str(st.st_dev)],
            ['st_nlink',str(st.st_nlink)],
            ['st_uid',str(st.st_uid)],
            ['st_gid',str(st.st_gid)],
            ['st_size',str(st.st_size)],
            ['st_atime',str(st.st_atime)],
            ['st_mtime',str(st.st_mtime)],
            ['st_ctime',str(st.st_ctime)],
            ]
        return "\n".join(map(lambda x: ':'.join(x), values))
