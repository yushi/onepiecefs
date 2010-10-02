import re


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
