import datetime
import json

import pymongo.errors
import zmq
from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from pymongo import MongoClient


class DataStorage(StoppableThread):
    def __init__(self,
                gd2_pipeline_host="127.0.0.1",
                gd2_pipeline_port=5050,
                database_host='127.0.0.1',
                database_port=27017,
                time_limit=1000):
        try:
            self.client = MongoClient(host=database_host, port=database_port, serverSelectionTimeoutMS=5000)
        except pymongo.errors.ServerSelectionTimeoutError as e:
            log.error(e)
        self.server_status = self.client.admin.command("serverStatus")
        self.gd2_database = self.client['GD2']
        self.gd2_collection = self.gd2_database['messages']
        self.time_limit = time_limit
        self.host = gd2_pipeline_host
        self.port = gd2_pipeline_port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect('tcp://{}:{}'.format(self.host, self.port))
        self.socket.set(zmq.SUBSCRIBE, bytes("", 'utf-8'))
        log.info("Connected socket: {}".format(self.socket.get(zmq.IDENTITY)))
        self.gd2_collection.create_index("expire_at", expireAfterSeconds=0)

    def store_data(self, data_message):
        self.gd2_collection.insert_one(data_message)

    def run(self):
        while True:
            try:
                message = self.socket.recv()
                json_msg = json.loads(message)
                # Set the expiration time for the messages we are putting into the database
                if 'expire_at' in json_msg.keys():
                    log.warning('expiration time for incoming message was already set: {}, using value in message'.format(json_msg['expire_at']))
                else:
                    json_msg['expire_at'] = datetime.datetime.utcnow() + datetime.timedelta(seconds = self.time_limit)
                log.trace(json_msg)
                self.store_data(json_msg)
            except zmq.ZMQError:
                continue
            except Exception as e:
                log.info("Caught exception during data store ZMQ receive: {}".format(e))
                self.socket.close()
                self.context.destroy()
                self.gd2_collection.drop_index("expire_at_1")
                break

def run(gd2_pipeline_host="127.0.0.1", gd2_pipeline_port=5050, database_host='localhost', database_port=27017, time_limit=1000):
    data_store = DataStorage(gd2_pipeline_host=gd2_pipeline_host,
                            gd2_pipeline_port=gd2_pipeline_port,
                            database_host=database_host,
                            database_port=database_port,
                            time_limit=time_limit)
    data_store.run()
