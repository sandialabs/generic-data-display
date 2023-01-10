import asyncio
import json

import generic_data_display.pipeline.output_generators.openmct.dictionary_provider as openmct
import requests
from aiohttp import web
from generic_data_display.utilities.logger import log

_ROUTES = web.RouteTableDef()


@_ROUTES.get('/')
async def get_root(_):
    return web.Response(text="Hello World, I am GD2!")


# get available data streams
@_ROUTES.get('/config')
def get_config(request):
    log.debug(f"/config request received, respond with: {openmct.global_mct_dictionary}")
    return web.json_response(openmct.global_mct_dictionary)

def post_namespaces():
    session = requests.Session()
    session.trust_env = False
    data = {'namespaces': openmct.global_mct_namespaces}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    try:
        url = 'http://sidecar:3000/namespaces'
        log.debug(f"Posting namespaces: {openmct.global_mct_namespaces} to {url}")
        response = session.post(url, data=json.dumps(data), headers=headers, timeout=2)
    except:
        url = 'http://localhost:3000/namespaces'
        log.debug(f"Running outside of a docker container, posting namespaces: {openmct.global_mct_namespaces} to {url}")
        response = session.post(url, data=json.dumps(data), headers=headers, timeout=2)
    log.debug(f"Request sent: {response.request.body}")
    log.debug(f"Response status code: {response.status_code} | Response reason: {response.reason}")

@_ROUTES.get('/live')
async def websocket_handler(request):
    log.debug(f"/live request received, handling the request: {request}")
    await request.app['websocket_manager'].handle_request(request)


async def start_bg_tasks(app):
    app['data_fetcher'] = asyncio.create_task(app['websocket_manager'].run())


async def stop_bg_tasks(app):
    app['data_fetcher'].cancel()
    await app['data_fetcher']


async def close_processors(app):
    app['process_manager'].close()


async def close_sockets(app):
    await app['websocket_manager'].close_sockets()


def create_app(websocket_manager, process_manager):
    app = web.Application()

    app['websocket_manager'] = websocket_manager
    app['process_manager'] = process_manager

    app.add_routes(_ROUTES)

    app.on_startup.append(start_bg_tasks)
    app.on_shutdown.append(close_sockets)
    app.on_cleanup.append(close_processors)
    app.on_cleanup.append(stop_bg_tasks)

    return app
