
import asyncio
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

AIS_API_KEY = os.getenv("AIS_API_KEY")

async def main():
    uri = f"wss://aisstream.io/api/v1/stream?apikey={AIS_API_KEY}"

    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(message) 

if __name__ == "__main__":
    asyncio.run(main())
