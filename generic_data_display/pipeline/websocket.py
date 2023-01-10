import asyncio
import json
import queue
from collections import namedtuple

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.type_wrapper import JSONEncoder


import aiohttp
from aiohttp import web


class WebsocketClient:
    def __init__(self, ws):
        self._ws = ws
        self._topics = set()
        self._encoder = JSONEncoder()

    def subscribe(self, topic):
        log.debug(f'Websocket client subscribed to topic "{topic}"')
        self._topics.add(topic)

    def unsubscribe(self, topic):
        log.debug(f'Websocket client unsubscribed from topic "{topic}"')
        if topic in self.topics:
            self._topics.remove(topic)

    async def send(self, msg):
        if self._ws.closed:
            return
        if msg['topic'] in self._topics:
            await self._ws.send_json(msg, dumps=self._encoder.encode)

    @property
    def topics(self):
        return self._topics

    async def handle(self, app):
        try:
            async for ws_msg in self._ws:
                if ws_msg.type != aiohttp.WSMsgType.TEXT:
                    continue

                try:
                    msg = json.loads(ws_msg.data)
                except json.decoder.JSONDecodeError as err:
                    log.debug(f'Could not parse websocket message: {ws_msg.data}')
                    continue

                if 'cmd' not in msg.keys():
                    continue

                if msg['cmd'] == 'close':
                    log.debug(f'Websocket client closed connection')
                    break
                elif msg['cmd'] == 'subscribe' and 'topic' in msg.keys():
                    self.subscribe(msg['topic'])
                elif msg['cmd'] == 'unsubscribe' and 'topic' in msg.keys():
                    self.unsubscribe(msg['topic'])
        finally:
            await self.close("Socket Disconnecting")

    async def close(self, msg):
        log.debug("WE ARE CLOSING THE SOCKET WITH MSG: {}".format(msg))
        await self._ws.close(code=aiohttp.WSCloseCode.GOING_AWAY, message=msg)


class WebsocketManager(object):
    def __init__(self, **kwargs):
        self.clients = []
        self.output_queues = []
        # self.websocket_topic_dict = {}

    # def add_topic_listener(self, socket, topic):
    #     pass

    # def add_websocket(self, socket):
    #     pass

    def add_output_queues(self, output_queues):
        self.output_queues.extend(output_queues)

    async def handle_request(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        client = WebsocketClient(ws)

        self.clients.append(client)
        await client.handle(request.app)
        self.clients.remove(client)

    async def close_sockets(self):
        log.debug("WE ARE CLOSING ALL THE CLIENTS NOW")
        for client in self.clients:
            await client.close("Server Shutdown")

    async def run(self):
        try:
            while True:
                sleep_counter = 0
                for output_queue in self.output_queues:
                    try:
                        msg = output_queue.get(False, None)
                        for ws in self.clients:
                            await ws.send(msg)
                    except queue.Empty:
                        sleep_counter += 1
                if sleep_counter == len(self.output_queues):
                    await asyncio.sleep(5e-2)
        except asyncio.CancelledError:
            await self.close_sockets()
