#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This module defines classes for implementing HTTP/WSGI servers (Web servers).
Warning This is not recommended for production. It only implements basic security checks.
One class, Server or WSGI Server creates and listens at the HTTP 
socket, dispatching the requests to a handler.
"""

from __future__ import print_function
import io
try:
    import http.client as status
    from http.server import HTTPServer, BaseHTTPRequestHandler, \
        SimpleHTTPRequestHandler
    from socketserver import ThreadingMixIn
except:
    import httplib as status
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import ThreadingMixIn
import sys

__version__ = '1.0.0'


class Server(HTTPServer):

    """This class builds on the HTTPServer class. This is only a wrapper. The 
     server is accessible by the handler, typically through the handler’s
     server instance variable."""


class ThreadingServer(ThreadingMixIn, HTTPServer):

    """This class is identical to Server but uses threads to handle 
    requests by using the ThreadingMixIn. This is useful to handle web 
    browsers pre-opening sockets, on which Server would wait indefinitely."""


class SimpleHandler(SimpleHTTPRequestHandler):

    """This class serves files from the current directory and below, 
    directly mapping the directory structure to HTTP requests.
    A lot of the work, such as parsing the request, is done by the base 
    class BaseHandler. This class implements the do_GET() 
    and do_HEAD() functions."""


class BaseHandler(BaseHTTPRequestHandler):

    """This class is used to handle the HTTP requests that arrive at the
     server. By itself, it cannot respond to any actual HTTP requests; 
     it must be subclassed to handle each request method (e.g. GET or 
     POST). BaseHandler provides a number of class and instance
      variables, and methods for use by subclasses."""


class WSGIServer(HTTPServer):

    """This class builds on the HTTPServer class. But it's changed to a 
    WSGI server.This can work with any WSGI web framework. The 
     server is accessible by the handler, typically through the handler’s
     server instance variable."""

    def set_app(self, application):
        self.application = application


class WSGIHandler(BaseHTTPRequestHandler):

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

    def get_environ(self):
        env = {}

        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables

        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = io.StringIO(self.requestline)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        # Required CGI variables

        env['REQUEST_METHOD'] = self.requestline  # GET
        env['PATH_INFO'] = self.path  # /hello
        env['SERVER_NAME'] = self.client_address[0]  # localhost
        env['SERVER_PORT'] = str(self.client_address[1])  # 8888
        env['SCRIPT_NAME'] = __name__
        env['SERVER_PROTOCOL'] = self.request_version
        env['wsgi.version'] = '1.0.1'
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
