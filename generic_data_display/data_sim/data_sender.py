from generic_data_display.data_sim import http_sender, tcp_sender, zmq_sender
from generic_data_display.data_sim import data_generators

from generic_data_display.utilities.logger import log

class DataSender(object):
    """
    Parses the supplied config, determines the output connection type, and then
    sends data over that connection using the configured format.
    """

    _connection_dict = {
        "http": lambda config, generator: http_sender.HttpSender(config, generator),
        "tcp": lambda config, generator: tcp_sender.TcpSender(config, generator),
        "zmq": lambda config, generator: zmq_sender.ZmqSender(config, generator)
    }

    _generator_dict = {
        "kaitai_basic": lambda config: data_generators.KaitaiBasicDataGenerator(config),
        "kaitai_image": lambda config: data_generators.KaitaiImageDataGenerator(config),
        "protobuf_basic": lambda config: data_generators.ProtobufBasicDataGenerator(config),
        "json_image": lambda config: data_generators.JsonImageDataGenerator(config),
        "json_nested": lambda config: data_generators.JsonNestedDataGenerator(config),
        "json_telemetry": lambda config: data_generators.JsonTelemetryDataGenerator(config),
        "csv_image": lambda config: data_generators.CsvImageDataGenerator(config),
        "yaml_image": lambda config: data_generators.YamlImageDataGenerator(config),
        "http_json_basic": lambda config: data_generators.HttpJsonBasicDataGenerator(config),
        "http_xml_basic": lambda config: data_generators.HttpXmlBasicDataGenerator(config),
        "tcp_xml_basic": lambda config: data_generators.TcpXmlBasicDataGenerator(config),
        "zmq_xml_basic": lambda config: data_generators.ZmqXmlBasicDataGenerator(config)
    }

    def __init__(self, config):
        """
        Initializes the DataSender using the supplied config

        :param config: A json object describing the "connection" and the "data" to send
        """
        self._config = config
        self._generator = self._generator_dict[self._config["data"]["type"]](self._config["data"])
        self._sender = self._connection_dict[self._config["connection"]["type"]](self._config["connection"],
                                                                                 self._generator)

    def close(self):
        log.info("shutting down data sender")
        self._sender.close()
        self._generator.close()

    def run(self):
        log.info("running data sender")
        self._sender.run()
