import asyncio
import json
import websockets
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
API_KEY = os.getenv("AIS_API_KEY")

# saving fused data by ship in this dict
cache = {}


def get_subscribe_message():
    return json.dumps(
        {
            "APIKey": API_KEY,
            "BoundingBoxes": [
                [[-90, -180], [90, 180]]
            ],  # all the world coordinates, can be changed
            "FilterMessageTypes": [
                "PositionReport",
                "ShipStaticData",
                "StandardClassBPositionReport",
                "LongRangeAisBroadcastMessage",
            ],
        }
    )


async def process_message(message):
    msg_type = message.get("MessageType")
    print(f"📡 Recibido tipo: {msg_type}")

    if msg_type not in [
        "PositionReport",
        "ShipStaticData",
        "StandardClassBPositionReport",
    ]:
        return None  # ignoring non relevant mssg

    data = message.get("Message", {}).get(msg_type)
    if not data:
        return None

    user_id = str(data.get("UserID") or data.get("UserIdentifier"))
    if not user_id:
        print("❌ Without UserID, ignored.")
        return None

    print(f"Processing menssage Ship ID: {user_id}")

    if user_id not in cache:
        cache[user_id] = {}

    cache[user_id].update(data)

    # returning snapshot fused by ship (user_id)
    return cache[user_id]


async def listen_and_process(process_fn, listen_seconds=30):
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
            await ws.send(get_subscribe_message())
            print("✅ Suscripction sent...")

            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < listen_seconds:
                try:
                    raw = await ws.recv()
                    msg = json.loads(raw)
                    fused_data = await process_message(msg)
                    if fused_data:
                        await process_fn(fused_data)
                except Exception as e:
                    print(f"⚠️ Error processing menssage: {e}")

    except Exception as e:
        print(f"❌ WebSocket error: {e}")


# import asyncio
# import json
# import websockets
# import os
# from dotenv import load_dotenv
# from datetime import datetime, timezone
# from websockets.exceptions import ConnectionClosedError, WebSocketException

# load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# API_KEY = os.getenv("AIS_API_KEY")


# def get_subscribe_message():
#     return json.dumps(
#         {
#             "APIKey": API_KEY,
#             "BoundingBoxes": [[[-90, -180], [90, 180]]],
#         }
#     )


# # para que no quede enchufado todo el tiempo, en el dag se indicara el tiempo


# async def listen_and_process(process_fn, listen_seconds=None):
#     try:
#         async with websockets.connect(
#             "wss://stream.aisstream.io/v0/stream"
#         ) as websocket:
#             await websocket.send(get_subscribe_message())
#             start_time = datetime.now()

#             async for message_json in websocket:
#                 try:
#                     message = json.loads(message_json)
#                     message_type = message.get("MessageType")
#                     data = message.get("Message", {}).get(message_type)

#                     if data and message_type in (
#                         "PositionReport",
#                         "StaticDataReport",
#                         "VoyageData",
#                     ):
#                         data["MessageType"] = message_type  # para saber de dónde vino
#                         await process_fn(data)

#                 except Exception as e:
#                     print(f"Error processing message: {e}")

#                 if listen_seconds is not None:
#                     elapsed = (datetime.now() - start_time).total_seconds()
#                     if elapsed > listen_seconds:
#                         print(f"Listened {listen_seconds} seconds, exiting...")
#                         break

#     except Exception as e:
#         print(f"Websocket connection failed: {e}")


# async def listen_and_process(process_fn, listen_seconds=None):
#     try:
#         async with websockets.connect(
#             "wss://stream.aisstream.io/v0/stream"
#         ) as websocket:
#             await websocket.send(get_subscribe_message())
#             start_time = datetime.now()

#             async for message_json in websocket:
#                 try:
#                     messages = json.loads(message_json)

#                     # if message.get("MessageType") == "PositionReport":
#                     #     data = message["Message"]["PositionReport"]
#                     #     if data:
#                     #         await process_fn(data)
#                     if isinstance(messages, list):
#                         for msg in messages:
#                             await process_fn(msg)
#                     elif isinstance(messages, dict):
#                         await process_fn(messages)
#                 except Exception as e:
#                     print(f"Error processing message: {e}")

#                 if listen_seconds is not None:
#                     elapsed = (datetime.now() - start_time).total_seconds()
#                     if elapsed > listen_seconds:
#                         print(f"Listened {listen_seconds} seconds, exiting...")
#                         break

#     except Exception as e:
#         print(f"Websocket connection failed : {e}")
