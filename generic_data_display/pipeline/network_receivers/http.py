import httplib2
import time

import requests.exceptions

from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.utilities.logger import log


class HttpReceiver(StoppableThread):
    """
    A class that describes how to receive data over HTTP.
    """

    def __init__(self, parser, **kwargs):
        super().__init__(name="HttpReceiver")

        log.info("Initializing the HTTP Receiver")
        config = {}
        config.update(kwargs)
        self.parser = parser  # TODO: How does this decide which parser to choose: JSON or XML???

        # Validate the configuration values.
        if not config["address"].strip():
            log.error("Address value missing from configuration, exiting.")
            exit(1)
        if not config["port"]:
            log.error("Port value missing from configuration, exiting.")
            exit(1)
        elif config["port"] < 0 or config["port"] > 65535:
            log.error("Port value must be an integer value between 0 - 65535, exiting.")
            exit(1)
        if not config["path"].strip():
            log.error("Path value missing from configuration, exiting.")
            exit(1)
        elif not config["path"].strip().startswith("/"):
            log.error("Path value must begin with a forward slash, exiting.")
            exit(1)
        if config["method"].upper() != "GET" and config["method"].upper() != "POST":
            log.error("Invalid HTTP method detected (expected GET or POST), exiting.")
            exit(1)
        if not config["rate_sec"]:
            log.error("Rate_sec value missing from configuration, exiting.")
            exit(1)
        elif config["rate_sec"] <= 0:
            log.error("Rate_sec must be a positive integer value, exiting.")
            exit(1)
        if not config["timeout_sec"]:
            log.error("Rate_sec must be a positive integer value, exiting.")
            exit(1)
        elif config["timeout_sec"] <= 0:
            log.error("Timeout_sec must be a positive integer value, exiting.")
            exit(1)
        if config["http_accept"] != "json" and config["http_accept"] != "xml":
            log.error("Invalid http_accept value detected (expected JSON or XML), exiting.")
            exit(1)

        # Store necessary configuration variables.
        self.type = config["type"].strip()
        self.address = config["address"].strip()
        self.port = config["port"]
        self.timeout_sec = config["timeout_sec"]
        self.method = config["method"].upper()
        self.path = config["path"].strip()
        self.rate_sec = config["rate_sec"]
        self.http_accept = config["http_accept"]
        if "post_request" not in config:
            self.post_request = ""
        else:
            self.post_request = config["post_request"].strip()

        # Determine the headers to send.
        self.headers = None
        if self.http_accept == "json":
            self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        elif self.http_accept == "xml":
            self.headers = {"Content-Type": "application/xml", "Accept": "text/xml, application/xml"}
        else:
            log.error("Invalid http_accept detected (expected JSON or XML), exiting.")
            exit(1)

        log.info("HTTP Receiver has been initialized")

    def close(self):
        log.info("Shut down HTTP Receiver")

    def run(self):
        log.info("Starting the HTTP Receiver")

        try:
            while True:
                # Build the target URL.
                url = self.type + "://" + self.address
                if self.port != "":
                    url = url + ":" + str(self.port)
                url = url + self.path

                # Connect to the server.
                try:
                    # Poll the HTTP endpoint.
                    http = httplib2.Http(timeout=self.timeout_sec)
                    if self.method == "GET":
                        (resp, content) = http.request(url, method="GET", headers=self.headers)
                    elif self.method == "POST":
                        (resp, content) = http.request(url, method="POST", headers=self.headers, body=self.post_request)
                    else:
                        msg = "Invalid HTTP method detected (expected GET or POST), exiting."
                        log.error(msg)
                        raise Exception(msg)

                    # Check the status code.
                    if resp.status < 200 or resp.status > 300:
                        log.error("Server responded with an unsuccessful status code (data will not be parsed): " +
                                  str(resp.status) + " - " + resp.reason)
                    else:
                        log.trace(f"Parsing a response of type {self.http_accept}")
                        self.parser.parse_from_bytes(content)

                except (requests.URLRequired,
                        requests.RequestException,
                        requests.TooManyRedirects) as e:
                    # Handle known fatal errors.
                    log.fatal("Fatal Error: " + str(e))
                    break
                except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout) as e:
                    # Handle known non-fatal errors.
                    log.error("Error occurred while polling an HTTP endpoint: " + str(e))
                except Exception as e:
                    # Handle all unknown (and unexpected) errors.
                    log.error("Unexpected exception thrown while polling an HTTP endpoint: " + str(e))

                # Sleep for the specified amount of time.
                time.sleep(self.rate_sec)

        except StopIteration:
            log.info("Interrupt received, stopping the HTTP Receiver")
        finally:
            self.close()
