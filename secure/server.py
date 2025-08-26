from http.server import SimpleHTTPRequestHandler, HTTPServer

index=b"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flag</title>
    </head>
    <body>
        <h1>{{flag}}</h1>
    </body>
    </html>
"""
flag="CTF{example_flag}"

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Write the HTML content
            self.wfile.write(index)
        else:
            # Fall back to default handler (serves files if available)
            super().do_GET()


def run(server_class=HTTPServer, handler_class=CustomHandler, port=80):
    server_address = ("127.0.0.1", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        flag = sys.argv[1]
    index = index.replace(b"{{flag}}", flag.encode())
    run()
