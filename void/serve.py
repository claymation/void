import http.server
import os
import socketserver


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def serve(root, port):
    Handler = http.server.SimpleHTTPRequestHandler

    oldcwd = os.getcwd()
    os.chdir(root)

    print("Listening for requests on http://localhost:{}/".format(port))

    with TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            httpd.server_close()
            os.chdir(oldcwd)
