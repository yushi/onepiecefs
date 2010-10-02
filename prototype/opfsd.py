import os
import sys
import BaseHTTPServer
import pickle
from optparse import OptionParser
from opfsutil import OPFSUtil

class OPFSD(BaseHTTPServer.HTTPServer):
    def __init__(self, *args):
        BaseHTTPServer.HTTPServer.__init__(self, *args)
        self.config = {
            'allow': None,
            'conf_file': None,
            'basedir': None
            }

    def update_allow_addrs(self):
        self.config['allow'] = OPFSUtil.get_peer_addrs(self.config['conf_file'])
        if self.config['allow'] == None:
            OPFSUtil.create_peers_file(path)
            print "please setup %s" % (path)
            sys.exit(-1)

    def set_config(self, config):
        self.config = config

class OPFSDHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_CONFUPDATE(self):
        if self.client_address[0] == '127.0.0.1':
            self.server.update_allow_addrs()

    def do_PROPFIND(self):
        if not self.is_peer_allowd():
            self.send_forbidden()
            return
        # provide stat(2)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        realpath = self.get_realpath(self.path)
        try:
            stat = os.stat(realpath)
            self.wfile.write(pickle.dumps(stat))
            print stat
        except Exception, info:
            print info
            self.wfile.write(pickle.dumps(None))

    def do_GET(self):
        if not self.is_peer_allowd():
            self.send_forbidden()
            return
        self.parse_parameter()
        # provide read(2)/readdir(3)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        realpath = self.get_realpath(self.actual_path)

        if os.path.isfile(realpath):
            # get file data and write
            f = open(realpath, 'r')

            #FIXME replase offset and size to Range request header?
            if 'offset' in self.query:
                # seek to offset
                f.seek(int(self.query['offset']))
            if 'size' in self.query:
                # read by size
                self.wfile.write(f.read(int(self.query['size'])))
                print "read part"
            else:
                # read all
                self.wfile.write(f.read())
                print "read all"

        elif os.path.isdir(realpath):
            # get dir list and write 1 entry 1 line
            dirlist = "\n".join(os.listdir(realpath))
            self.wfile.write(dirlist)
            print dirlist

    def send_forbidden(self):
        self.send_response(403)
        self.end_headers()

    def is_peer_allowd(self):
        return self.client_address[0] in self.server.config['allow']

    def get_realpath(self, path):
        basedir = self.server.config['basedir']
        return basedir + os.path.abspath(path)

    def parse_parameter(self):
        self.actual_path = self.path
        self.query = {}
        query_pos = self.path.find('?')
        if query_pos != -1:
            # '?' found
            self.actual_path = self.path[0:query_pos]
            if len(self.path) == query_pos + 1:
                # '?' found but last char is '?' ex. "/hoge?"
                print "illegal querystring"
            else:
                #  parse querystring
                query_str = self.path[query_pos + 1::]
                for q in query_str.split('&'):
                    key, val = q.split('=')
                    self.query[key] = val


def sighup_handler(signum, frame):
    # update allow list when sighup received
    update_allow_addrs()

    
def run(server_class=OPFSD,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):

    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port",
                      help="listen port", default="5656")
    parser.add_option("-d", "--debug", dest="debug",
                      help="listen port", default=False)
    parser.add_option("-c", "--conf", dest="conf_file",
                      help="config file for peers", default="~/.opfs_peers")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        print "usage: python opfsd.py <publish path>"
        sys.exit(-1)

    conf_file = os.path.realpath(os.path.expanduser(options.conf_file))
    basedir = args.pop()

    server_address = ('', int(options.port))
    print "listen port: %s" % (options.port)


    httpd = server_class(server_address, OPFSDHandler)
    httpd.set_config({
            'basedir': basedir,
            'allow': None,
            'conf_file': conf_file
            })

    httpd.update_allow_addrs()

    httpd.serve_forever()

run()
