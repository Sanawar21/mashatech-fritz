import asyncio


async def main():
    from app.clients import KleinanzeigenClient, TelegramClient
    from app.server import WebSocketServer

    from app.messages import SendOfferMessage

    from app.exceptions import InvalidAdException

    ka_client = KleinanzeigenClient()
    tg_client = TelegramClient()
    server = WebSocketServer()
    server.start()

    if not server.is_running:
        await server.start()
    self_connect_cycle = 0

    while True:
        self_connect_cycle += 1
        if self_connect_cycle > 500:
            await server.self_connect()
            self_connect_cycle = 0

        await asyncio.sleep(1)
        ads = ka_client.get_fritz_ads()

        for ad in ads:
            try:
                message = SendOfferMessage(ad)
            except InvalidAdException:
                continue

            await server.send_message(message)
            tg_client.send_ad_alert(ad)

if __name__ == "__main__":
    pass
