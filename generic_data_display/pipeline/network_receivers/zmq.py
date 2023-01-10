from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.utilities.logger import log

import zmq


class ZmqReceiver(StoppableThread):
    """Handles receiving data over a zmq socket

    Parses the provided config to determine the type of zmq connection
    socket to create in order to successfully connect to a data generator.
    Hooks up the data receipt call of the provided socket with a provided
    parser's parse_from_bytes function in order to convert received data into
    usable output in the rest of the processing pipeline.
    """

    zmq_map_dict = {
        "SUB": zmq.SUB,
        "PULL": zmq.PULL,
    }

    def __init__(self, parser, **kwargs):
        super().__init__(name="ZmqReceiver")

        log.info("Initializing the Zmq Receiver")
        config = {}
        config.update(kwargs)
        self.parser = parser

        self.context = zmq.Context()
        self.socket_type = config['socket_type']
        self.socket = self.context.socket(self.zmq_map_dict[self.socket_type])
        self.method = config["method"]

        if self.method == "bind":
            self.socket.bind('tcp://{}:{}'.format(config['address'], config['port']))
            log.info("Bound socket: {}".format(self.socket.underlying))
        elif self.method == "connect":
            self.socket.connect('tcp://{}:{}'.format(config['address'], config['port']))
            if self.socket_type == "SUB":
                self.socket.set(zmq.SUBSCRIBE, bytes(config['topic'], 'utf-8'))
            log.info("Connected socket: {}".format(self.socket.get(zmq.IDENTITY)))
        else:
            log.error("Bad method type, exiting")
            exit(1)

    def close(self):
        self.socket.close()
        self.context.destroy()
        log.info("Shut down Zmq Receiver")

    def run(self):
        log.info("Starting the Zmq Receiver")

        try:
            while self.is_running():
                try:
                    self.parser.parse_from_bytes(self.socket.recv(zmq.NOBLOCK))
                except zmq.ZMQError:
                    continue
        finally:
            self.close()
