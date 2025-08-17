import asyncio
import json
import websockets
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
API_KEY = os.getenv("AIS_API_KEY")

cache = {}


def get_subscribe_message():
    return json.dumps(
        {
            "APIKey": API_KEY,
            "BoundingBoxes": [[[-90, -180], [90, 180]]],
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
        return None

    data = message.get("Message", {}).get(msg_type)
    if not data:
        return None

    user_id = str(data.get("UserID") or data.get("UserIdentifier"))
    if not user_id:
        print("❌ Without UserID, ignored.")
        return None

    if user_id not in cache:
        cache[user_id] = {}

    cache[user_id].update(data)

    return cache[user_id]


async def listen_and_print(listen_seconds=10):
    try:
        async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
            await ws.send(get_subscribe_message())
            print("✅ Suscripto al stream")

            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < listen_seconds:
                try:
                    raw = await ws.recv()
                    msg = json.loads(raw)
                    fused_data = await process_message(msg)
                    if fused_data:
                        print(
                            json.dumps(fused_data, indent=2)
                        )  # ✅ Imprimimos el snapshot fusionado
                except Exception as e:
                    print(f"⚠️ Error procesando mensaje: {e}")

    except Exception as e:
        print(f"❌ Error WebSocket: {e}")


if __name__ == "__main__":
    asyncio.run(listen_and_print())
