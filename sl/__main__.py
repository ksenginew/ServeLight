from sl.server import *
if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', '-a', help='App for Run as WSGI Server'
                        )
    parser.add_argument(
        '--port', '-p'
        action='store',
        default=8000,
        type=int,
        nargs='?',
        help='Specify alternate port [default: 8000]',
    )
    parser.add_argument(
        '--threading', '-t'
        action='store',
        default=False,
        type=bool,
        nargs='?',
        help='uses threads to handle requests',
    )
    parser.add_argument(
        '--multiprocessing', '-m'
        action='store',
        default=False,
        type=bool,
        nargs='?',
        help='uses processes to handle requests',
    )
    args = parser.parse_args()
    if args.threading:
        server_class = ThreadingWSGIServer
    elif args.multiprocessing:
        server_class = ForkingWSGIServer
    else:
        server_class = WSGIServer
    if args.app:
        (module, application) = args.app.split(':')
        module = __import__(module)
        application = getattr(module, application)
        httpd = make_server('', args.port, application,
                            server_class=server_class)
        print('WSGIServer: Serving HTTP on port {PORT} ...\n'.format(
            PORT=args.port))
        try:
            httpd.serve_forever()
        except:
            print('    WSGIServer: Server Stopped')
    else:
        httpd = make_server('', args.port, demo_app, server_class=server_class)
        print("Serving HTTP on", httpd.host, "port", httpd.port, "...")
        try:
            httpd.serve_forever()
        except:
            print('    WSGIServer: Server Stopped')
