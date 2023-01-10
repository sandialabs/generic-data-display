import socket
import time

from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.utilities.logger import log


class TcpReceiver(StoppableThread):
    """
    A class that describes how to receive data over a TCP socket
    Requires a "parser" object on initialization that must implement a
    parseIoByteStream function to interface with the socket file created
    by the tcp receive socket.
    """
    def __init__(self, parser, **kwargs):
        super().__init__(name="TcpReceiver")

        log.info("Initializing the Tcp Receiver")
        config = {}
        config.update(kwargs)
        self.parser = parser

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (config["address"], config["port"])
        self.method = config["method"]
        self.reconnect_attempts = config["reconnect_attempts"]
        self.reconnect_interval_sec = config["reconnect_interval_sec"]

        if self.method == "bind":
            log.info("Binding {} to {}".format(self.server_address[0], self.server_address[1]))
            self.socket.bind(self.server_address)
            self.socket.listen(1)
            self.receive_socket, self.client_address = self.socket.accept()
        elif self.method == "connect":
            log.info("Connecting {} to {}".format(self.server_address[0], self.server_address[1]))
            self.socket.connect(self.server_address)
            self.receive_socket = self.socket
        else:
            log.error("Bad method type, exiting")
            exit(1)

        self.sock_file = self.receive_socket.makefile(mode='rb')

    def reconnect(self):
        log.info("Lost TCP connection, attempting to reconnect...")
        reconnect_counter = 0
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            log.info("Attempting reconnect: {}/{} with {} second reconnection interval".format(reconnect_counter+1, self.reconnect_attempts, self.reconnect_interval_sec))
            try:
                if self.method == "bind":
                    log.info("Attempting to rebind {} to {}".format(self.server_address[0], self.server_address[1]))
                    self.socket.bind(self.server_address)
                    self.socket.listen(1)
                    self.receive_socket, self.client_address = self.socket.accept()
                elif self.method == "connect":
                    log.info("Attempting to reconnect {} to {}".format(self.server_address[0], self.server_address[1]))
                    self.socket.connect(self.server_address)
                    self.receive_socket = self.socket
                self.sock_file = self.receive_socket.makefile(mode='rb')
            except socket.error as e:
                log.debug("ERROR: {}".format(e))
                if reconnect_counter == self.reconnect_attempts-1:
                    log.info("Unable to reconnect to socket {}:{}".format(self.server_address[0], self.server_address[1]))
                    return False
                time.sleep(self.reconnect_interval_sec)
            else:
                log.info("Successfully reconnected to socket {}:{}".format(self.server_address[0], self.server_address[1]))
                return True
            reconnect_counter += 1

    def close(self):
        log.info("Shutting down the Tcp Receiver")
        self.socket.close()
        self.receive_socket.close()
        self.sock_file.flush()
        self.sock_file.close()
        log.info("Shut down Tcp Receiver")

    def run(self):
        log.info("Starting the Tcp Receiver")

        reconnected = False
        while self.is_running():
            try:
                self.socket.sendall(b'heatbeat')
                self.parser.parse_io_byte_stream(self.sock_file)
                if reconnected:
                    reconnected = False
            except socket.error as e:
                log.error(e)
                reconnected = self.reconnect()
                if not reconnected:
                    self.close()
                    break
                else:
                    self.parser.reset_io_byte_stream()
            except StopIteration:
                try:
                    self.socket.sendall(b'heatbeat')
                except socket.error as e:
                    log.error(e)
                    reconnected = self.reconnect()
                    if not reconnected:
                        self.close()
                        break
                    else:
                        self.parser.reset_io_byte_stream()
                else:
                    log.info("Input stream ended")
                    self.close()
            except Exception as e:
                log.error("Caught Exception {} in tcp reciever".format(e))
                self.close()
                break


