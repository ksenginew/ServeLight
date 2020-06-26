from sl.server import *
if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', '-a', help='App for Run as WSGI Server'
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
        httpd = make_server('', args.port, demo_app)
        sa = httpd.socket.getsockname()
        print("Serving HTTP on", sa[0], "port", sa[1], "...")
        try:
            httpd.serve_forever()
        except:
            print('    WSGIServer: Server Stopped')
