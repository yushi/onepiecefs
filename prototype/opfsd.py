import os
import sys
import tornado.httpserver
import tornado.ioloop
import tornado.web
from optparse import OptionParser
from opfsutil import OPFSUtil
import urllib

debug = False
config = {}

def debug_print(msg):
    global debug
    if debug:
        print msg


def update_allow_addrs():
    config['allow'] = \
        OPFSUtil.get_peer_addrs(config['conf_file'])


class OPFSDHandler(tornado.web.RequestHandler):
    def do_CONFUPDATE(self):
        # for config reload
        if self.client_address[0] == '127.0.0.1':
            update_allow_addrs()

    def stat_response(self, path):
        # provide stat(2)
        self.set_status(200)
        self.set_header('Content-type', 'text/plain')

        realpath = self.get_realpath(path)
        try:
            st = os.stat(realpath)
            self.write(OPFSUtil.stat2str(st))
            debug_print(st)
            return
        except Exception, info:
            debug_print(info)
            return

    def readdir_response(self, path):
        self.set_status(200)
        self.set_header('Content-type', 'text/plain')

        realpath = self.get_realpath(self.actual_path)

        if not os.path.isdir(realpath):
            pass
        # get dir list and write 1 entry 1 line
        dirlist = "\n".join(os.listdir(realpath))
        self.write(dirlist)
        debug_print(dirlist)

    def read_response(self, path):
        # provide read(2)/readdir(3)
        self.set_status(200)
        self.set_header('Content-type', 'text/plain')

        realpath = self.get_realpath(path)

        if os.path.isfile(realpath):
            # get file data and write
            f = open(realpath, 'r')

            #FIXME replase offset and size to Range request header?
            if 'offset' in self.query:
                # seek to offset
                f.seek(int(self.query['offset']))
            if 'size' in self.query:
                # read by size
                self.write(f.read(int(self.query['size'])))
                debug_print("read part")
            else:
                # read all
                self.write(f.read())
                debug_print("read all")

    def get(self, *args, **kargs):
        debug_print(self.request)
        if not self.is_peer_allowd():
            self.send_forbidden()
            return
        self.parse_parameter()

        if not 'mode' in self.query:
            return

        if self.query['mode'] == 'stat':
            self.stat_response(self.actual_path)
        elif self.query['mode'] == 'readdir':
            self.readdir_response(self.actual_path)
        elif self.query['mode'] == 'read':
            self.read_response(self.actual_path)


        return

    def send_forbidden(self):
        self.set_status(403)

    def is_peer_allowd(self):
        return self.request.remote_ip in config['allow']

    def get_realpath(self, path):
        basedir = config['basedir']
        return basedir + os.path.abspath(path)

    def parse_parameter(self):
        self.path = self.request.uri
        self.actual_path = urllib.unquote(os.path.abspath(self.path))
        self.query = {}
        query_pos = self.path.find('?')
        if query_pos != -1:
            # '?' found
            self.actual_path = urllib.unquote(os.path.abspath(self.path[0:query_pos]))
            if len(self.path) == query_pos + 1:
                # '?' found but last char is '?' ex. "/hoge?"
                debug_print("illegal querystring")
            else:
                #  parse querystring
                query_str = self.path[query_pos + 1::]
                for q in query_str.split('&'):
                    key, val = q.split('=')
                    self.query[key] = val


def sighup_handler(signum, frame):
    # update allow list when sighup received
    update_allow_addrs()


def run(handler_class=OPFSDHandler):
    global config
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port",
                      help="listen port", default="5656")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",
                      help="debug")
    parser.add_option("-c", "--conf", dest="conf_file",
                      help="config file for peers", default="~/.opfs_peers")

    (options, args) = parser.parse_args()
    global debug
    debug = options.debug

    if len(args) != 1:
        print "usage: python opfsd.py <publish path>"
        sys.exit(-1)

    conf_file = os.path.realpath(os.path.expanduser(options.conf_file))
    basedir = args.pop()

    #server_address = ('', int(options.port))
    debug_print("listen port: %s" % (options.port))

    application = tornado.web.Application([
            (r".*", handler_class),
            ])

    config = {
        'basedir': basedir,
        'allow': None,
        'conf_file': conf_file
            }
    update_allow_addrs()
    if config['allow'] == None:
        OPFSUtil.create_peers_file(path)
        print "please setup %s" % (path)
        sys.exit(-1)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(int(options.port))
    tornado.ioloop.IOLoop.instance().start()

run()
