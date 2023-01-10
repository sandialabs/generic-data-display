import zmq
import logging


class ZmqSender(object):

    zmq_map_dict = {
        "PUB": zmq.PUB,
        "PUSH": zmq.PUSH,
        "REP": zmq.REP
    }

    def __init__(self, config, generator):
        logging.info("init zmq sender")

        self.context = zmq.Context()
        self.socket = self.context.socket(self.zmq_map_dict[config['socket_type']])
        self.socket.bind("tcp://{}:{}".format(config['address'], config['port']))

        logging.info("Bound socket: {}".format(self.socket.get(zmq.IDENTITY)))

        self._generator = generator
        self._connection = None
        self._client_address = None

    def close(self):
        self.socket.close()
        self.context.destroy()

    def run(self):
        logging.info("running zmq sender")

        for data in self._generator.generate_data():
            self.socket.send(data)
