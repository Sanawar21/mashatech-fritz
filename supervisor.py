import subprocess
import asyncio
import websockets
import logging
import signal
import sys

# Global variable to track the subprocess
process = None


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
    global process

    # Start main.py
    process = subprocess.Popen(["python3", "main.py"])
    logging.info("Started main.py")

    asyncio.sleep(10)  # Wait for main.py to start

    while True:
        await asyncio.sleep(1)
        # Run WebSocket client
        server_running = await ping_server("ws://localhost:8765")

        # If server is not running, terminate main.py and restart with --load-state
        if not server_running:
            process.terminate()
            process.wait()
            logging.info("Restarting main.py with --load-state")
            process = subprocess.Popen(["python3", "main.py", "--load-state"])


def handle_shutdown(signum, frame):
    global process
    if process is not None:
        logging.info("Terminating main.py...")
        process.terminate()
        process.wait()
    logging.info("Supervisor shutting down")
    sys.exit(0)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Run the supervisor
    try:
        asyncio.run(supervisor())
    except SystemExit:
        pass
    except Exception as e:
        logging.error(f"Unexpected error in supervisor: {e}")
