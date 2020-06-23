#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module defines classes for implementing HTTP/WSGI servers (Web servers).
Warning This is not recommended for production. It only implements basic security checks.
One class, Server or WSGI Server creates and listens at the HTTP 
socket, dispatching the requests to a handler.
"""

from __future__ import print_function
try:
    import http.client as status
    from http.server import HTTPServer as Server, BaseHTTPRequestHandler as BaseHandler, SimpleHTTPRequestHandler as SimpleHandler
    from socketserver import ThreadingMixIn
    from io import StringIO
    from urllib import parse as urllib
except:
    import httplib as status
    from BaseHTTPServer import HTTPServer as Server, BaseHTTPRequestHandler as BaseHandler
    from SimpleHTTPServer import SimpleHTTPRequestHandler as SimpleHandler
    from SocketServer import ThreadingMixIn
    from StringIO import StringIO
    import urllib
import sys

__version__ = '1.1.3'


class ThreadingServer(ThreadingMixIn, Server):

    """This class is identical to Server but uses threads to handle 
    requests by using the ThreadingMixIn. This is useful to handle web 
    browsers pre-opening sockets, on which Server would wait indefinitely."""

class WSGIServer(Server):

    """This class builds on the HTTPServer class. But it's changed to a 
    WSGI server.This can work with any WSGI web framework. The 
     server is accessible by the handler, typically through the handler’s
     server instance variable."""

    def set_app(self, application):
        self.application = application

    def get_app(self):
        return self.application


class WSGIHandler(BaseHandler):

    """This class is used to handle the HTTP requests that arrive at the
     server. BaseHandler provides a number of class and instance
      variables, and methods for use by subclasses."""

    def do_GET(self):
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body

        result = self.server.application(env, self.start_response)

        # Construct a response and send it back to the client

        self.finish_response(result)
    
    def uni(self,string):
        try:
            return unicode(string, "utf-8")
        except:
            return string
            
    def get_environ(self):
        env = {}

        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables

        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO(self.uni(self.requestline))
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variables
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['REQUEST_METHOD'] = self.requestline  # GET
        env['SERVER_NAME'] = self.server.server_name  # localhost
        env['SERVER_PORT'] = str(self.server.server_port)  # 8888
        env['SCRIPT_NAME'] = ""
        env['SERVER_PROTOCOL'] = self.request_version
        env['SERVER_SOFTWARE'] = self.server_version
        env['REQUEST_METHOD'] = self.command
        if '?' in self.path:
            path,query = self.path.split('?',1)
        else:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.unquote(path)
        env['QUERY_STRING'] = query
        if isinstance(self.client_address, tuple):
            host = self.address_string()
            if host != self.client_address[0]:
                env['REMOTE_HOST'] = host
            env['REMOTE_ADDR'] = self.client_address[0]
            env['REMOTE_PORT'] = self.client_address[1] 
        if self.headers.get('content-type') is None:
            env['CONTENT_TYPE'] = self.headers.get_content_type()
        else:
            env['CONTENT_TYPE'] = self.headers['content-type']

        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        for k, v in self.headers.items():
            k=k.replace('-','_').upper(); v=v.strip()
            if k in env:
                continue                    # skip content length, type,etc.  
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        return env

    def start_response(
        self,
        status,
        response_headers,
        exc_info=None,
        ):
        self.send_response(int(status[:status.find(' ')]),
                           status[status.find(' ') + 1:])
        for header in response_headers:
            self.send_header(header[0], header[1])
        self.end_headers()

    def finish_response(self, result):
        for item in result:
            self.wfile.write(item)

    def version_string(self):
        """Return the server software version string."""

        return 'ServerLight'  # +__version__


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):

    """This class is identical to WSGIServer but uses threads to handle 
    requests by using the ThreadingMixIn. This is useful to handle web 
    browsers pre-opening sockets, on which Server would wait indefinitely."""


def make_server(server_address, application):
    server = ThreadingWSGIServer(server_address, WSGIHandler)
    server.set_app(application)
    return server


if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', '-a', help='App for Run as WSGI Server'
                        )
    parser.add_argument('--bind', '-b', metavar='ADDRESS',
                        help='Specify alternate bind address [default: all interfaces]'
                        )
    parser.add_argument('--directory', '-d', default=os.getcwd(),
                        help='Specify alternative directory [default:current directory]'
                        )
    parser.add_argument(
        'port',
        action='store',
        default=8000,
        type=int,
        nargs='?',
        help='Specify alternate port [default: 8000]',
        )
    args = parser.parse_args()
    os.chdir(args.directory)
    if args.app:
        (module, application) = args.app.split(':')
        module = __import__(module)
        application = getattr(module, application)
        httpd = make_server(('', args.port), application)
        print('WSGIServer: Serving HTTP on port {PORT} ...\n'.format(PORT=args.port))
        try:
            httpd.serve_forever()
        except:
            print('    WSGIServer: Server Stopped')
    else:
        httpd = ThreadingServer(('', args.port), SimpleHandler)
        print('SimpleServer : serving at port', args.port)
        try:
            httpd.serve_forever()
        except:
            print('    SimpleServer: Server Stopped')
