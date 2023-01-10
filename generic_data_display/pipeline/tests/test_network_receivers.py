import json
import multiprocessing as mp
import os
import time
import unittest
import signal

from generic_data_display.data_sim import data_sender
from generic_data_display.pipeline.data_parsers import csv as _csv
from generic_data_display.pipeline.data_parsers import json as _json
from generic_data_display.pipeline.data_parsers import kaitai, protobuf
from generic_data_display.pipeline.data_parsers import xml as _xml
from generic_data_display.pipeline.data_parsers import yaml as _yaml
from generic_data_display.pipeline.network_receivers import tcp
from generic_data_display.utilities.logger import log

client_config_base_directory = "generic_data_display/data_sim/resources/data_sim_configs/"
gd2_config_base_directory = "generic_data_display/data_sim/resources/pipeline_configs/"

class TestNetworkReceivers(unittest.TestCase):
    def setUp(self):

        # The names from the sender and reciever configs need to match!
        self.sender_configs = {
            'tcp_csv_image': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_csv_image.json")),
            'tcp_json_image': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_json_image.json")),
            'tcp_kaitai_image': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_kaitai_image.json")),
            'tcp_proto_basic': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_proto_basic.json")),
            'tcp_xml_basic': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_xml_basic.json")),
            'tcp_yaml_image': self.load_config(os.path.join(client_config_base_directory, "sim_config_tcp_yaml_image.json"))
            }
        self.reciever_configs = {
            'tcp_csv_image': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_csv_image.json")),
            'tcp_json_image': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_json_image.json")),
            'tcp_kaitai_image': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_kaitai_image.json")),
            'tcp_proto_basic': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_proto_basic.json")),
            'tcp_xml_basic': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_xml_basic.json")),
            'tcp_yaml_image': self.load_config(os.path.join(gd2_config_base_directory, "backend_config_tcp_yaml_image.json"))
            }

    def load_config(self, json_file):
        with open(json_file, 'r') as f:
            config = json.load(f)
        return config

    def test_tcp_disconnection_reconnection(self):
        pass

        # TODO (mjfadem): The TCP connection/socket isn't fully dying, there is a interuption and then
        # an immediate reconnection. This should be enough for testing in the short term but we'll
        # need to revisit this in the future.
        '''
        log.setLevel("TRACE")

        for name, config in self.sender_configs.items():
            log.debug(f"Running {name} test...")
            parser_data_queue = mp.Queue()
            tcp_sender = data_sender.DataSender(self.sender_configs[name]['config'][0])
            if "csv" in name:
                tcp_receiver = tcp.TcpReceiver(_csv.CSVParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            elif "json" in name:
                tcp_receiver = tcp.TcpReceiver(_json.JsonParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            elif "kaitai" in name:
                tcp_receiver = tcp.TcpReceiver(kaitai.KaitaiParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            elif "proto" in name:
                tcp_receiver = tcp.TcpReceiver(protobuf.ProtobufParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            elif "xml" in name:
                tcp_receiver = tcp.TcpReceiver(_xml.XmlParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            elif "yaml" in name:
                tcp_receiver = tcp.TcpReceiver(_yaml.YamlParser(parser_data_queue,
                                                                **self.reciever_configs[name]['config'][0].get("data", {})),
                                                                **self.reciever_configs[name]['config'][0].get("connection", {}))
            else:
                raise KeyError('Unknown parser type')


            # Multiprocessing
            sender_process = mp.Process(target=tcp_sender.run)
            receiver_process = mp.Process(target=tcp_receiver.run)
            sender_process.start()
            sender_pid = sender_process.pid
            receiver_process.start()
            receiver_pid = receiver_process.pid


            log.debug("Sleeping for 5 seconds to let the processes spin up...")
            time.sleep(5)

            queue_size_pre_kill = parser_data_queue.qsize()

            log.debug("Sleeping for 5 seconds to let the sender process shut down...")
            os.kill(sender_pid, signal.SIGINT)
            sender_process.join()
            time.sleep(5)

            queue_size_post_kill = parser_data_queue.qsize()

            log.debug("Sleeping for 5 seconds to starve the reciever process of data...")
            time.sleep(5)

            sender_process = mp.Process(target=tcp_sender.run)
            sender_process.start()
            sender_pid = sender_process.pid
            log.debug("Sleeping for 5 seconds to restart the sender process...")
            time.sleep(5)
            queue_size_post_reconnect = parser_data_queue.qsize()

            try:
                self.assertGreater(queue_size_post_reconnect, queue_size_post_kill)
            except:
                log.debug("We failed the queue size test!")
                log.debug(f"Data Queue Length Pre-Kill: {queue_size_pre_kill}")
                log.debug(f"Data Queue Length Post-Kill: {queue_size_post_kill}")
                log.debug(f"Data Queue Length Post-Reconnect: {queue_size_post_reconnect}")
                log.debug(f"{queue_size_post_reconnect} > {queue_size_post_kill}? {queue_size_post_reconnect > queue_size_post_kill}")
            finally:
                log.debug("Terminating sender and receiver processes so everything is cleaned up...")
                os.kill(receiver_pid, signal.SIGINT)
                receiver_process.join()
                os.kill(sender_pid, signal.SIGINT)
                sender_process.join()
                time.sleep(5)
        '''


if __name__ == '__main__':
    unittest.main()
