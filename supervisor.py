import subprocess
import asyncio
import websockets
import logging


async def ping_server(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                await websocket.send('{"type": "keepAlive", "sendReply": true}')
                response = await websocket.recv()
                if response != "pong":
                    raise websockets.exceptions.ConnectionClosedError
                await asyncio.sleep(5)  # Ping every 5 seconds
            except (websockets.exceptions.ConnectionClosedError, asyncio.TimeoutError):
                logging.error("No response from server, restarting main.py")
                return False
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                return False
    return True


async def supervisor():
    while True:
        # Start main.py
        process = subprocess.Popen(["python", "main.py"])
        logging.info("Started main.py")

        # Run WebSocket client
        server_running = await ping_server("ws://localhost:8765")

        # If server is not running, terminate main.py and restart with --load-state
        if not server_running:
            process.terminate()
            process.wait()
            logging.info("Restarting main.py with --load-state")
            process = subprocess.Popen(["python3", "main.py", "--load-state"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(supervisor())
