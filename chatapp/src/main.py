import os
import asyncio
import logging
import aioredis
from aioredis.client import PubSub, Redis
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(os.environ['HOST_IP'])
HOST_IP = os.environ['HOST_IP']

app = FastAPI()

html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>ChatApp</title>
    </head>
    <body>
        <h1>ChatApp</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="text" autocomplete="off"/>
            <button>送る</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://{HOST_IP}:8000/ws");
            ws.onmessage = function(event) {{
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            }};
            function sendMessage(event) {{
                var input = document.getElementById("text")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }}
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await redis_connector(websocket)

async def redis_connector(websocket: WebSocket):
    async def consumer_handler(redis: Redis, websocket: WebSocket):
        try:
            while True:
                message = await websocket.receive_text()
                if message:
                    await redis.publish("chatapp", message)
        except WebSocketDisconnect:
            logger.info(f"Client #{id(websocket)} disconnected")
        except Exception as e:
            logger.error(f"Exception: {e}")


    async def producer_handler(pubsub: PubSub, websocket: WebSocket):
        await pubsub.subscribe("chatapp")
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    await websocket.send_text(message.get('data'))
        except Exception as e:
            logger.error(f"Exception: {e}")

    redis = await get_redis()
    pubsub = redis.pubsub()

    consumer_task = consumer_handler(redis=redis, websocket=websocket)
    producer_task = producer_handler(pubsub=pubsub, websocket=websocket)

    _, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        logger.debug(f"Canceling task: {task}")
        task.cancel()


async def get_redis():
    return await aioredis.from_url('redis://172.18.0.100:6379', encoding="utf-8", decode_responses=True)
