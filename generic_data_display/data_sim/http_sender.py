from http.server import BaseHTTPRequestHandler, HTTPServer
import logging


class HttpSender:
    def __init__(self, config, generator):
        logging.info("Initializing the HTTP sender")

        self.host = config['address']
        self.port = config['port']
        self.endpoint = config['endpoint']
        self._generator = generator

        # Set default values.
        if not self.host:
            self.host = '127.0.0.1'
        if not self.port:
            self.port = 8081
        if not self.endpoint:
            self.endpoint = "/"
        elif not self.endpoint.startswith("/"):
            logging.fatal("Endpoint must start with a forward slash.")

    def close(self):
        pass  # Nothing to do here.

    def run(self):
        logging.info("Starting the HTTP sender on http://%s:%s", self.host, self.port)

        webServer = HTTPServer((self.host, self.port), self.create_server(self._generator, self.endpoint))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("HTTP server stopped.")

    def create_server(self, generator, endpoint):
        # Nested class.
        class HttpHandler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self._generator = generator
                self.endpoint = endpoint
                super(HttpHandler, self).__init__(*args, **kwargs)

            ####################
            # GET handler.
            ####################
            def do_GET(self):
                if self.path == self.endpoint:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(self._generator.generate_data(), "utf-8"))
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(bytes("Path not found: [" + self.path + "]", "utf-8"))

            ####################
            # POST handler.
            ####################
            def do_POST(self):
                if self.path == self.endpoint:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(self._generator.generate_data(), "utf-8"))
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(bytes("Path not found: [" + self.path + "]", "utf-8"))

        return HttpHandler
