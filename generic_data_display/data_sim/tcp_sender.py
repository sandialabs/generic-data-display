import socket
import sys

from generic_data_display.utilities.logger import log

class TcpSender(object):
    def __init__(self, config, generator):
        log.info("init tcp sender")

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (config['address'], config['port'])
        self._socket.bind(server_address)
        self._socket.listen(1)
        log.info("Bound socket to: {}".format(self._socket.getsockname()))

        self._generator = generator
        self._connection = None
        self._client_address = None

    def close(self):
        log.info("Shutting down the tcp sender")
        self._socket.close()

    def run(self):
        log.info("running tcp sender")
        try:
            self._connection, self._client_address = self._socket.accept()
            for data in self._generator.generate_data():
                self._connection.sendall(data)
        except KeyboardInterrupt:
            log.info("Caught TCP Sender keyboard interrupt.")
            if self._connection:
                self._connection.close()
        finally:
            if self._connection:
                self._connection.close()
