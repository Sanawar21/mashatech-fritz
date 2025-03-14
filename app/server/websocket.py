import websockets
import requests
import asyncio
import logging

from ..messages import MessageFactory
from ..messages.base import OutgoingMessage
from ..exceptions import InvalidIncomingMessageException, InvalidOfferStatusException


class WebSocketServer:
    def __init__(self, host, port, ctx):
        self.host = host
        self.port = port
        self.server = None
        self.ctx = ctx
        self.message_factory = MessageFactory()

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

    async def handle_client(self, websocket, path):
        # Add client to the set of connected clients
        self.clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    message = self.message_factory.create_message(message)
                except InvalidIncomingMessageException:
                    logging.info(f"Invalid incoming message: {message}")
                    continue
                try:
                    message.process(self.ctx)
                except InvalidOfferStatusException:
                    logging.info(
                        f"Error: Invalid offer status. Message: {message}")
                if message.response:
                    await self.send_message(message.response)

        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            # Remove client from the set of connected clients when they disconnect
            self.clients.remove(websocket)

    async def start(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        self.is_running = True

    async def send_message(self, message: OutgoingMessage):
        """Send a message to all connected clients """
        for client in self.clients:
            try:
                await client.send(message.to_json())
            except websockets.exceptions.ConnectionClosedError:
                self.clients.remove(client)

    async def stop(self):
        """Close the server and all client connections"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False

    async def self_connect(self):
        """
        fix for an uncertain bug where the server stops sending messages until a new client connects.
        """
        if self.is_running:
            async with websockets.connect(self.public_address):
                await asyncio.sleep(15)
