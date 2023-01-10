import csv
import datetime
import io
import json
import logging
import os
import struct
import time
from base64 import b64encode

import yaml
from numpy import random

from generic_data_display.data_sim.resources.data_definitions.protobuf import \
    basic_protobuf_pb2


class KaitaiBasicDataGenerator(object):
    """
    Creates a basic packed binary blob with an int and a timestamp string
    """

    def __init__(self, config):
        logging.info("init kaitai basic generator")
        self._step = config['range_step']
        self._min = config['range_start']
        self._max = config['range_stop']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._min, self._max, self._step):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                cur_time_enc = cur_time.encode()
                cur_time_len = len(cur_time_enc)
                logging.debug("Sending item {} with len {} at time {}".format(i, cur_time_len, cur_time))
                yield struct.pack(f'!ii{cur_time_len}s', i, cur_time_len, cur_time_enc)
            if not self._loop:
                break


class KaitaiImageDataGenerator(object):
    """
    Creates a basic packed binary blob with a byte size, image, and a timestamp string
    Message is formatted: row, col, byte_size, bytes_per_pixel, counter, timestamp, image bytes
    """

    def __init__(self, config):
        logging.info("init kaitai image generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                cur_time_enc = cur_time.encode()
                cur_time_len = len(cur_time_enc)
                size = random.choice(self._image_sizes)
                image_id = self._image_sizes.index(size)
                byte_size = size * size * self._bytes_per_pixel
                image = random.random((size, size, self._bytes_per_pixel)) * 255
                logging.debug("Sending image {} with size {} at time {}".format(image_id, size, cur_time))
                yield struct.pack(f'!iiliii{cur_time_len}s', size, size, byte_size, self._bytes_per_pixel, image_id,
                                  cur_time_len, cur_time_enc) + image.astype('uint8').tobytes()


class ProtobufBasicDataGenerator(object):
    """
    Creates a basic packed binary blob with an int and a timestamp string
    """

    def __init__(self, config):
        logging.info("init protobuf basic generator")
        self._step = config['range_step']
        self._min = config['range_start']
        self._max = config['range_stop']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._prepend_message_size = config['prepend_message_size']

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._min, self._max, self._step):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                cur_time_enc = cur_time.encode()
                logging.debug("Sending item {} with len {} at time {}".format(i, len(cur_time), cur_time))
                message = basic_protobuf_pb2.ExampleData()
                message.counter = i
                message.date = cur_time_enc
                message_string = message.SerializeToString()
                message_size = len(message_string)
                if self._prepend_message_size:
                    message_string = message_size.to_bytes(4, byteorder='big') + message_string

                yield message_string
            if not self._loop:
                break


class JsonImageDataGenerator(object):
    """
    Creates a basic packed binary blob with a byte size, image, and a timestamp string
    Message is formatted: row, col, byte_size, bytes_per_pixel, counter, timestamp, image bytes
    """

    def __init__(self, config):
        logging.info("init json image generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                size = random.choice(self._image_sizes)
                image_id = self._image_sizes.index(size)
                image = random.random((size, size, self._bytes_per_pixel)) * 255
                logging.debug("Sending image {} with size {} at time {}".format(image_id, size, cur_time))
                yield json.dumps(dict(
                    time=cur_time,
                    image_id=image_id,
                    image_edge=int(size),
                    image=b64encode(image.astype('uint8').tobytes()).decode()
                )).encode()


class JsonNestedDataGenerator(object):
    """
    Creates a basic packed binary blob with a byte size, image, and a timestamp string
    Message is formatted: row, col, byte_size, bytes_per_pixel, counter, timestamp, image bytes
    """

    def __init__(self, config):
        logging.info("init json nested generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1

    def close(self):
        pass

    def gen_stream(self, cur_time, size):
        image = random.random((size, size, self._bytes_per_pixel)) * 255
        return dict(
            time=cur_time,
            width=int(size),
            height=int(size),
            image=b64encode(image.astype('uint8').tobytes()).decode()
        )

    def generate_data(self):
        while True:
            msg = dict(stream=dict())
            cur_time = None
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                size = random.choice(self._image_sizes)
                msg['stream'][i] = self.gen_stream(cur_time, size)

            logging.debug(f"Sending image with {len(msg['stream'])} number of images at time {cur_time}")
            yield json.dumps(msg).encode()


class JsonTelemetryDataGenerator(object):
    """
    Creates a basic packed binary blob with a byte size, image, and a timestamp string
    Message is formatted: row, col, byte_size, bytes_per_pixel, counter, timestamp, image bytes
    """

    def __init__(self, config):
        logging.info("init json telemetry generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1
        self._rng = random.default_rng()

    def close(self):
        pass

    def gen_stream(self, cur_time, size, index):
        image = random.random((size, size, self._bytes_per_pixel)) * 255
        return dict(
            time=cur_time,
            width=int(size),
            height=int(size),
            index=int(index),
            image=b64encode(image.astype('uint8').tobytes()).decode()
        )

    def generate_data(self):
        while True:
            msg = dict(stream=dict(),
                       metadata=dict())
            cur_time = None
            size = random.choice(self._image_sizes)
            image_subset_id = self._image_sizes.index(size)
            msg['metadata']['image_subset_id'] = "id_" + str(image_subset_id)
            msg['metadata']['temperature'] = self._rng.uniform(60, 90)
            msg['metadata']['nominal_value'] = 0 if self._rng.uniform(0, 1) > 1.5 else 1
            msg['metadata']['voltage'] = self._rng.uniform(5.5, 6.0)
            msg['metadata']['msg_time'] = str(datetime.datetime.now())
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                msg['stream'][i] = self.gen_stream(cur_time, size, i)

            logging.debug(f"Sending image with {len(msg['stream'])} number of images at time {cur_time}")
            yield json.dumps(msg).encode()


class YamlImageDataGenerator(object):
    """
    Creates a basic packed binary blob with a byte size, image, and a timestamp string
    Message is formatted: row, col, byte_size, bytes_per_pixel, counter, timestamp, image bytes
    """

    def __init__(self, config):
        logging.info("init yaml image generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                size = random.choice(self._image_sizes)
                image_id = self._image_sizes.index(size)
                image = random.random((size, size, self._bytes_per_pixel)) * 255
                logging.debug("Sending image {} with size {} at time {}".format(image_id, size, cur_time))
                yield yaml.safe_dump(dict(
                    time=cur_time,
                    image_id=image_id,
                    image_edge=int(size),
                    image=b64encode(image.astype('uint8').tobytes()).decode()
                ), explicit_start=True, explicit_end=True).encode()


class CsvImageDataGenerator(object):
    def __init__(self, config):
        logging.info("init csv image generator")
        self._range = config['range']
        self._sleep_time = config['ms_between_send'] / 1000
        self._loop = config['loop_forever']
        self._image_sizes = config['image_sizes']
        self._bytes_per_pixel = 3 if config['color'] else 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            for i in range(self._range):
                time.sleep(self._sleep_time)
                cur_time = str(datetime.datetime.now())
                size = random.choice(self._image_sizes)
                image_id = self._image_sizes.index(size)
                image = random.random((size, size, self._bytes_per_pixel)) * 255
                logging.debug("Sending image {} with size {} at time {}".format(image_id, size, cur_time))
                csv_data = str(cur_time) + ',' + str(image_id) + ',' + str(int(size)) + ',' + b64encode(image.astype('uint8').tobytes()).decode() + "\n"
                yield csv_data.encode()


class HttpJsonBasicDataGenerator(object):
    """
    Creates a basic JSON response that can be served by an HTTP server.
    """

    def __init__(self, config):
        self.status = 200
        self.increment = 1

    def generate_data(self):
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        response = json.dumps(
            dict(
                format="json",
                tx=ts,
                status=str(self.status),
                increment=str(self.increment)
            ),
            indent=2)

        # Update the data values.
        if self.status == 200:
            self.status = 400
        else:
            self.status = 200
        self.increment += 1

        # Return the generated JSON string.
        return response


class HttpXmlBasicDataGenerator(object):
    """
    Creates a basic JSON response that can be served by an HTTP server.
    """

    def __init__(self, config):
        self.status = 200
        self.increment = 1

    def generate_data(self):
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

        # TODO: Use an xml generator instead of hand-crafting the data string once xml parse support is added.
        response = ('<test>\n'
                    '  <format>xml</format>\n'
                    '  <ts>' + ts + '</ts>\n'
                    '  <status>' + str(self.status) + '</status>\n'
                    '  <increment>' + str(self.increment) + '</increment>\n'
                    '</test>')

        # Update the data values.
        if self.status == 200:
            self.status = 400
        else:
            self.status = 200
        self.increment += 1

        # Return the generated XML string.
        return response


class TcpXmlBasicDataGenerator(object):
    """
    Creates a basic JSON response that can be served by an HTTP server.
    """

    def __init__(self, config):
        self.status = 200
        self.increment = 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            time.sleep(1)  # Sleep for 1 second.
            now = datetime.datetime.now()
            ts = now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

            # TODO: Use an xml generator instead of hand-crafting the data string once xml parse support is added.
            msg = ('<test>\n'
                   '  <format>xml</format>\n'
                   '  <ts>' + ts + '</ts>\n'
                   '  <status>' + str(self.status) + '</status>\n'
                   '  <increment>' + str(self.increment) + '</increment>\n'
                   '</test>'
                   '\x00')  # EOF character required!!!
            response = msg.encode()

            # Update the data values.
            if self.status == 200:
                self.status = 400
            else:
                self.status = 200
            self.increment += 1

            # Return the generated XML string.
            yield response


class ZmqXmlBasicDataGenerator(object):
    """
    Creates a basic JSON response that can be served by an HTTP server.
    """

    def __init__(self, config):
        self.status = 200
        self.increment = 1

    def close(self):
        pass

    def generate_data(self):
        while True:
            time.sleep(1)  # Sleep for 1 second.
            now = datetime.datetime.now()
            ts = now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

            # TODO: Use an xml generator instead of hand-crafting the data string once xml parse support is added.
            msg = ('<test>\n'
                   '  <format>xml</format>\n'
                   '  <ts>' + ts + '</ts>\n'
                   '  <status>' + str(self.status) + '</status>\n'
                   '  <increment>' + str(self.increment) + '</increment>\n'
                   '</test>')
            response = msg.encode()

            # Update the data values.
            if self.status == 200:
                self.status = 400
            else:
                self.status = 200
            self.increment += 1

            # Return the generated XML string.
            yield response
