import http.server
import socketserver
import os

os.chdir("/Users/tanigutirei/Web_GL_Test2/Web_GL_Test2")


with socketserver.TCPServer(('127.0.0.1', 8000), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()