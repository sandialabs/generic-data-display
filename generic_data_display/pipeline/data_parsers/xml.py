from generic_data_display.pipeline.utilities.timer import Timer
from generic_data_display.pipeline.utilities.access_wrapper import AccessWrapper

from generic_data_display.utilities.logger import log

from ast import literal_eval
from io import StringIO
from lxml import etree
import xmltodict



class XmlParser(object):
    """
    XML Parser!

    Config:
        - schema: path to an XML Schema file
        - message_delimiter_byte: Byte used to separate messages (for TCP connections only).
    """

    def __init__(self, push_queue, **kwargs):
        log.info("Initializing the XML Parser")

        self.push_queue = push_queue
        self.config = {}
        self.config.update(kwargs)

        # Determine the path to the schema file (if one exists).
        self.schema = None
        if "schema" in self.config.keys():
            with open(self.config["schema"], 'r') as handle:
                xmlschema_doc = etree.parse(handle)
                self.schema = etree.XMLSchema(xmlschema_doc)

        # Parse the TCP delimiter character, or use b'\x00' if none was defined.
        self.message_delimiter_byte = b'\x00'
        if "message_delimiter_byte" in self.config.keys():
            if self.config["message_delimiter_byte"].startswith("\\"):
                self.message_delimiter_byte = literal_eval("b'" + self.config["message_delimiter_byte"] + "'")
            else:
                self.message_delimiter_byte = self.config["message_delimiter_byte"].encode("UTF-8")

        # Verify that the delimiter character is only 1-byte in size.
        if len(self.message_delimiter_byte) != 1:
            log.error("XML delimiter can only be 1-byte in size.")
            raise ValueError('XML delimiter is too large (must only be 1-byte in size).')

    def _validate(self, xml_msg):
        if self.schema:
            try:
                doc = etree.parse(xml_msg)
                return self.schema.validate(doc)
            except Exception as e:
                log.warn("XML msg triggered exception during validation.")
                log.debug(f"Error: {e}")
                log.debug(f"XML message: {xml_msg}")
                return False
        return True

    def reset_io_byte_stream(self):
        pass

    def parse_io_byte_stream(self, io_stream):
        timer = Timer()
        with timer('XML Parser (from I/O byte stream'):
            # Convert bytes to a String IO object (containing the XML document).
            xml_msg_string = ""
            while True:
                byte = io_stream.read(1)
                if byte == self.message_delimiter_byte:
                    break
                else:
                    xml_msg_string = xml_msg_string + byte.decode("utf-8")

            xml_msg_stringio = StringIO(xml_msg_string)

            # Validate the XML document.
            if not self._validate(xml_msg_stringio):
                log.debug(f"XML failed validation: {xml_msg_string}")
                return

            # Convert the XML document to a dictionary.
            xml_dict = xmltodict.parse(xml_msg_string)

            # Send the data to the queue.
            self.push_queue.put(AccessWrapper(xml_dict, timer=timer))

    def parse_from_bytes(self, obj_bytes):
        timer = Timer()
        with timer('XML Parser (from bytes)'):
            # Convert bytes to a String IO object (containing the XML document).
            xml_msg_string = obj_bytes.decode("utf-8")
            xml_msg_stringio = StringIO(xml_msg_string)

            # Validate the XML document.
            if not self._validate(xml_msg_stringio):
                log.debug(f"XML failed validation: {xml_msg_string}")
                return

            # Convert the XML document to a dictionary.
            xml_dict = xmltodict.parse(xml_msg_string)

            # Send the data to the queue.
            self.push_queue.put(AccessWrapper(xml_dict, timer=timer))
