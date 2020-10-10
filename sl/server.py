"""Server that implements the Python WSGI protocol (PEP 3333)

This is both an example of how WSGI can be implemented, and a basis for running
simple web applications on a local machine, such as might be done when testing
or debugging an application.  It has not been reviewed for security issues,
however, and we strongly recommend that you use a "real" web server for
production use.

For example usage, see the 'if __name__=="__main__"' block at the end of the
module.  See also the BaseHTTPServer module docs for other API information.
"""

from __future__ import print_function

import sys
import os
import socket
from .handlers import SimpleHandler
from platform import python_implementation
try:  # Py3
    import http.client as status
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn
    from urllib import parse as urllib
    PY2 = False
except ImportError:  # Py2
    import httplib as status
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from SocketServer import ThreadingMixIn
    import urllib
    PY2 = True

try:
    from socketserver import ForkingMixIn  # Forking Supported (Py3)
    forking = True
except ImportError:
    try:
        from SocketServer import ForkingMixIn  # Forking Supported (Py2)
        forking = True
    except ImportError:
        class ForkingMixIn(ThreadingMixIn):
            pass  # Forking Not Supported
        forking = False

import logging
logger = logging.getLogger(__name__)

try:
    import ssl
except ImportError:

    class SSL(object):
        def __getattr__(self, name):
            raise RuntimeError("SSL support unavailable")

    ssl = SSL()

__version__ = "3.0.1"
__all__ = ['WSGIServer', 'ThreadingWSGIServer', 'ForkingWSGIServer',
           'WSGIRequestHandler', 'demo_app', 'make_server', 'software_version', ]


server_version = "ServeLight/" + __version__
sys_version = python_implementation() + "/" + sys.version.split()[0]
software_version = server_version + ' ' + sys_version

try:
    af_unix = socket.AF_UNIX
except AttributeError:
    af_unix = None


class ServerHandler(SimpleHandler):

    server_software = software_version

    def close(self):
        try:
            self.request_handler.log_request(
                self.status.split(' ', 1)[0], self.bytes_sent
            )
        finally:
            SimpleHandler.close(self)


class WSGIServer(HTTPServer):

    """
    BaseHTTPServer that implements the Python WSGI protocol
    Simple single-threaded, single-process WSGI server.
    """

    application = None
    multithread = False
    multiprocess = False

    def __init__(self, server_address=('', None), handler=None, fd=None, ssl_context=None, *args, **kwargs):

        if not handler:
            handler = WSGIRequestHandler

        # copied from werkzeug    :copyright: 2007 Pallets    #:license: BSD-3-Clause
        if server_address[0].startswith("unix://"):
            self.address_family = socket.AF_UNIX
        # Fix for IPv6 addresses. # from bottlepy
        elif ':' in server_address[0] and getattr(self, 'address_family') == socket.AF_INET and hasattr(socket, "AF_INET6"):
            self.address_family = socket.AF_INET6

        if fd is not None:  # copied from werkzeug    :copyright: 2007 Pallets    #:license: BSD-3-Clause
            real_sock = socket.fromfd(
                fd, self.address_family, socket.SOCK_STREAM)
            server_address[1] = 0

        # copied from werkzeug    :copyright: 2007 Pallets    #:license: BSD-3-Clause
        server_address = get_sockaddr(server_address[0], int(
            server_address[1]), self.address_family)

        # remove socket file if it already exists
        # copied from werkzeug    :copyright: 2007 Pallets    #:license: BSD-3-Clause
        if self.address_family == af_unix and os.path.exists(server_address):
            os.unlink(server_address)

        HTTPServer.__init__(self, server_address, handler, *args, **kwargs)

        self.shutdown_signal = False
        self.host = self.socket.getsockname()[0]
        self.port = self.socket.getsockname()[1]

        # Patch in the original socket.
        if fd is not None:  # copied from werkzeug    :copyright: 2007 Pallets    #:license: BSD-3-Clause
            self.socket.close()
            self.socket = real_sock
            self.server_address = self.socket.getsockname()

        if ssl_context:  # copied from werkzeug and edited    :copyright: 2007 Pallets    #:license: BSD-3-Clause
            if isinstance(ssl_context, tuple) or isinstance(ssl_context, list):
                sock = self.socket
                protocol = None
                certfile = ssl_context[0]
                if len(ssl_context) > 1:
                    keyfile = ssl_context[1]
                else:
                    keyfile = certfile
                if len(ssl_context) > 2:
                    protocol = ssl_context[2]
                else:
                    try:
                        protocol = ssl.PROTOCOL_TLS_SERVER
                    except AttributeError:
                        # Python <= 3.5 compat
                        protocol = ssl.PROTOCOL_SSLv23
                # If we are on Python 2 the return value from socket.fromfd
                # is an internal socket object but what we need for ssl wrap
                # is the wrapper around it :(
                #
                if PY2 and not isinstance(sock, socket.socket):
                    sock = socket.socket(
                        sock.family, sock.type, sock.proto, sock)
                self.socket = ssl.wrap_socket(
                    sock, keyfile=keyfile, certfile=certfile, ssl_version=protocol, server_side=True)

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['wsgi.multithread'] = self.multithread
        env['wsgi.multiprocess'] = self.multiprocess
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST'] = ''
        env['CONTENT_LENGTH'] = ''
        env['SCRIPT_NAME'] = ''

    def get_app(self):
        return self.application

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        self.shutdown_signal = False
        try:
            HTTPServer.serve_forever(self)
        except KeyboardInterrupt as e:
            self.server_close()  # Prevent ResourceWarning: unclosed socket # from bottlepy
            raise e


class WSGIRequestHandler(BaseHTTPRequestHandler):

    """A request handler that implements WSGI dispatching."""

    server_version = "ServerLight/" + __version__

    def get_environ(self):
        env = self.server.base_environ.copy()
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = self.rfile
        env['wsgi.error'] = sys.stderr
        env['wsgi.run_once'] = False
        env['SERVER_PROTOCOL'] = self.request_version
        env['SERVER_SOFTWARE'] = self.server_version
        env['REQUEST_METHOD'] = self.command
        env['SCRIPT_NAME'] = ""

        if '?' in self.path:
            path, query = self.path.split('?', 1)
        else:
            path, query = self.path, ''
        try:
            env['PATH_INFO'] = urllib.parse.unquote(path, 'iso-8859-1')
        except:
            # "urllib.parse.unquote(path, 'iso-8859-1')" changed
            env['PATH_INFO'] = urllib.unquote(path)
        env['QUERY_STRING'] = query

        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host

        if not self.client_address:
            env['REMOTE_ADDR'] = "<local>"
        elif isinstance(self.client_address, str):
            env['REMOTE_ADDR'] = self.client_address
        else:
            env['REMOTE_ADDR'] = self.client_address[0]

        env['REMOTE_PORT'] = self.client_address[1]

        try:
            if self.headers.typeheader is None:
                env['CONTENT_TYPE'] = self.headers.type
            else:
                env['CONTENT_TYPE'] = self.headers.typeheader
        except:
            if self.headers.get('content-type') is None:
                env['CONTENT_TYPE'] = self.headers.get_content_type()
            else:
                env['CONTENT_TYPE'] = self.headers['content-type']

        length = self.headers.get('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for k, v in self.headers.items():
            k = k.replace('-', '_').upper()
            v = v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v
        return env

    def get_stderr(self):
        return sys.stderr

    def do_GET(self):

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ(),
            multithread=False,
        )
        handler.request_handler = self      # backpointer for logging
        handler.run(self.server.get_app())

    def do_POST(self):

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ(),
            multithread=False,
        )
        handler.request_handler = self      # backpointer for logging
        handler.run(self.server.get_app())

    def address_string(self):  # Prevent reverse DNS lookups please. # from bottlepy
        return self.client_address[0]

    def log_request(self, *args, **kw):  # from bottlepy
        if not self.quiet:
            return BaseHTTPRequestHandler.log_request(*args, **kw)


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):

    """This class is identical to WSGIServer but uses threads to handle 
    requests by using the ThreadingMixIn. This is useful to handle web 
    browsers pre-opening sockets, on which Server would wait indefinitely.
    """
    multithread = True
    daemon_threads = True


class ForkingWSGIServer(ForkingMixIn, WSGIServer):

    """A WSGI server that does forking.
    This class is identical to WSGIServer but handle each request in a new process 
    using the ForkingMixIn. This is useful to handle web 
    browsers pre-opening sockets, on which Server would wait indefinitely.
    """
    multiprocess = False
    forking = forking


def get_sockaddr(host, port, family):
    """Return a fully qualified socket address that can be passed to
    :func:`socket.bind`."""
    # copied from werkzeug
    #:copyright: 2007 Pallets
    #:license: BSD-3-Clause
    if family == af_unix:
        return host.split("://", 1)[1]
    try:
        res = socket.getaddrinfo(
            host, port, family, socket.SOCK_STREAM, socket.IPPROTO_TCP
        )
    except socket.gaierror:
        return host, port
    return res[0][4]


def demo_app(environ, start_response):
    try:
        from StringIO import StringIO
    except:
        from io import StringIO
    stdout = StringIO()
    print("Hello world!", file=stdout)
    print(file=stdout)
    h = sorted(environ.items())
    for k, v in h:
        print(k, '=', repr(v), file=stdout)
    start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])
    return [stdout.getvalue().encode("utf-8")]


def make_server(
    host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler
):
    """Create a new WSGI server listening on `host` and `port` for `app`"""
    server = server_class((host, port), handler_class)
    server.set_app(app)
    return server
