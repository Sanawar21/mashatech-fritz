import websockets
import requests
import asyncio
import datetime
import pytz

from .msg_handler import IncommingMessageHandler
from .response import OutgoingResponse


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.message_handler = IncommingMessageHandler()

        self.clients = set()
        self.is_running = False
        self.public_address = self.__get_public_address()

    def __get_public_address(self):
        try:
            response = requests.get('https://api.ipify.org')
            if response.status_code == 200:
                return f"ws://{response.text}:{self.port}"
            else:
                return "Error: Unable to retrieve IP address."
        except requests.RequestException as e:
            return f"Error: {e}"

    def get_date_time():
        """Returns current german time in the format: 1st January, 2021. Friday 12:00:00"""
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        german_timezone = pytz.timezone("Europe/Berlin")
        german_time = utc_now.astimezone(german_timezone)

        def get_day_suffix(day):
            if 4 <= day <= 20 or 24 <= day <= 30:
                return "th"
            else:
                return ["st", "nd", "rd"][day % 10 - 1]

        formatted_date_time = german_time.strftime(
            f"%-d{get_day_suffix(german_time.day)} %B, %Y. %A %H:%M:%S"
        )

        if formatted_date_time.startswith('0'):
            formatted_date_time = german_time.strftime(
                f"%#d{get_day_suffix(german_time.day)} %B, %Y. %A %H:%M:%S"
            )

        return formatted_date_time

    async def handle_client(self, websocket, path):
        # Add client to the set of connected clients
        self.clients.add(websocket)
        print(f"{websocket.remote_address} connected.")
        try:
            async for message in websocket:
                # TODO: Implement message handling
                response = self.message_handler.handle_message(message)
                await websocket.send(response)

        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Remove client from the set of connected clients when they disconnect
            self.clients.remove(websocket)
            print(f"{websocket.remote_address} disconnected.")

    async def start(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"WebSocket server started at {self.host}:{self.port}")
        self.is_running = True

    async def send_message(self, message):
        """Send a message to all connected clients """
        for client in self.clients:
            await client.send(message)

    async def stop(self):
        """Close the server and all client connections"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")
            self.is_running = False

    async def self_connect(self):
        """
        fix for an uncertain bug where the server stops sending messages until a new client connects. 
        """
        if self.is_running:
            print("self-connecting...")
            async with websockets.connect(self.public_address) as ws:
                await asyncio.sleep(15)
