import os
import sys
import BaseHTTPServer
import pickle

class OPFSDHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_PROPFIND(self):
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
            


        
    def do_GET(self):
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
                query_str = self.path[query_pos+1::]
                for q in query_str.split('&'):
                    key, val = q.split('=')
                    self.query[key] = val
        
def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    
    server_address = ('', 8000)
    httpd = server_class(server_address, OPFSDHandler)

    if len(sys.argv) != 2:
        print "usage: python opfsd.py <publish path>"
        sys.exit(-1)
    basedir = sys.argv.pop()

    httpd.config = {
        'basedir': basedir,
        }
    httpd.serve_forever()

run()
