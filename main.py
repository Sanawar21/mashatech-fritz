import asyncio


async def main():
    from app.clients import KleinanzeigenClient, TelegramClient
    from app.server import WebSocketServer
    from app.models import Counter
    from app.cache import MessageIDCache

    from app.messages import SendOfferMessage, CheckOfferStatusMessage

    from app.exceptions import InvalidAdException

    ka_client = KleinanzeigenClient()
    tg_client = TelegramClient()

    msg_cache = MessageIDCache()

    server = WebSocketServer('0.0.0.0', 8765)

    # # initialize counters
    # status_check_counter = Counter(0, 5, 0)
    pending_deletion_counter = Counter(48, 0, 0)
    accepted_deletion_counter = Counter(24, 0, 0)
    self_connect_counter = Counter(0, 5, 0)

    # testing counters
    status_check_counter = Counter(0, 1, 0)
    # pending_deletion_counter = Counter(48, 0, 0)
    # accepted_deletion_counter = Counter(24, 0, 0)
    # self_connect_counter = Counter(0, 5, 0)

    await server.start()
    print(f"Server started at {server.public_address}")

    # start counters
    status_check_counter.start()
    pending_deletion_counter.start()
    accepted_deletion_counter.start()
    self_connect_counter.start()

    while True:

        if self_connect_counter.is_finished():
            await server.self_connect()
            self_connect_counter.restart()

        await asyncio.sleep(1)

        # send new add offers
        ads = ka_client.get_fritz_ads()
        for ad in ads:
            try:
                message = SendOfferMessage(ad)
                print(message)
            except InvalidAdException:
                continue

            await server.send_message(message)
            tg_client.send_ad_alert(ad)

        # check status of offers
        if status_check_counter.is_finished():
            print("Checking offer status")
            cached_ids = msg_cache.read_n_day_old(2)
            print(cached_ids)
            for id_ in cached_ids:
                print(id_)
                message = CheckOfferStatusMessage(id_.message_id)
                await server.send_message(message)
            status_check_counter.restart()


if __name__ == "__main__":
    asyncio.run(main())
