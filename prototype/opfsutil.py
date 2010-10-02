import re
import os
import socket

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
