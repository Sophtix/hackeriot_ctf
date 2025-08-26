from http.server import SimpleHTTPRequestHandler, HTTPServer
import sys

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, password=None, **kwargs):
        self.JUMP_ROOT_PASSWORD = password
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/":
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # Write the HTML content with the dynamic password
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Department shares</title>
                </head>
                <body>
                    <h1>The credentials for telnet service are: root:{self.JUMP_ROOT_PASSWORD}</h1>
                </body>
                </html>
            """.encode('utf-8')
            self.wfile.write(html_content)
        else:
            # Fall back to default handler (serves files if available)
            super().do_GET()


def run(server_class=HTTPServer, handler_class=CustomHandler, port=8080, password=None):
    server_address = ("127.0.0.1", port)
    def handler(*args, **kwargs):
        return handler_class(*args, password=password, **kwargs)
    httpd = server_class(server_address, handler)
    print(f"Serving on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    import sys
    password = sys.argv[1] if len(sys.argv) > 1 else 'default_password'
    run(password=password)
