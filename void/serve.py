import http.server
import socketserver


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def serve(root, port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root, **kwargs)

    print("Listening for requests on http://localhost:{}/".format(port))

    with TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            httpd.server_close()
