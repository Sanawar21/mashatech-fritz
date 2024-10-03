import asyncio
import queue

from datetime import datetime
from urllib.parse import urlparse, parse_qs


async def main():
    from app.clients import KleinanzeigenClient, TelegramClient, AirtableClient
    from app.server import WebSocketServer
    from app.models import Counter
    from app.cache import MessageIDCache

    from app.messages.outgoing import SendOfferMessage, CheckOfferStatusMessage, DeleteOfferMessage, ReleasePaymentMessage

    from app.exceptions import InvalidAdException

    ka_client = KleinanzeigenClient()
    tg_client = TelegramClient()
    at_client = AirtableClient()

    msg_cache = MessageIDCache()

    server = WebSocketServer('0.0.0.0', 8765)

    pending_offers_queue = queue.Queue()
    offers_sent = 0

    # # initialize counters
    status_check_counter = Counter(0, 5, 0)
    offers_reset_counter = Counter(1, 0, 0)
    # pending_deletion_counter = Counter(48, 0, 0)
    accepted_deletion_counter = Counter(24, 0, 0)
    self_connect_counter = Counter(0, 5, 0)

    # testing counters
    # status_check_counter = Counter(0, 1, 0)
    pending_deletion_counter = Counter(0, 1, 0)
    accepted_deletion_counter = Counter(0, 0, 30)
    # self_connect_counter = Counter(0, 5, 0)

    await server.start()
    print(f"Server started at {server.public_address}")

    # start counters
    offers_reset_counter.start()
    status_check_counter.start()
    pending_deletion_counter.start()
    accepted_deletion_counter.start()
    self_connect_counter.start()

    while True:

        msg_cache.refresh()

        if self_connect_counter.is_finished():
            await server.self_connect()
            self_connect_counter.restart()

        await asyncio.sleep(1)

        # send new add offers
        ads = ka_client.get_fritz_ads()
        for ad in ads:
            try:
                message = SendOfferMessage(ad)
            except InvalidAdException:
                continue

            if offers_sent <= 50:
                await server.send_message(message)
                tg_client.send_ad_alert(ad)
                offers_sent += 1
            else:
                pending_offers_queue.put(message)

        # send pending offers
        while not pending_offers_queue.empty() and offers_sent <= 50:
            message = pending_offers_queue.get()
            await server.send_message(message)
            offers_sent += 1

        # reset offers sent counter
        if offers_reset_counter.is_finished():
            offers_sent = 0
            offers_reset_counter.restart()

        # check status of offers
        if status_check_counter.is_finished():
            cached_ids = msg_cache.read_n_day_old(2)
            for id_ in cached_ids:
                if id_.status != "paid":
                    message = CheckOfferStatusMessage(id_.message_id)
                    await server.send_message(message)
            status_check_counter.restart()

        # deletion of pending offers
        if pending_deletion_counter.is_finished():
            pending_offers = msg_cache.read_n_day_old(2, "pending")
            for offer in pending_offers:
                message = DeleteOfferMessage(offer.message_id)
                msg_cache.delete(offer.message_id)
                await server.send_message(message)
            pending_deletion_counter.restart()

        # deletion of accepted offers that are not paid
        if accepted_deletion_counter.is_finished():
            accepted_offers = msg_cache.read_n_day_old(1, "accepted")
            for offer in accepted_offers:
                message = DeleteOfferMessage(offer.message_id)
                msg_cache.delete(offer.message_id)
                await server.send_message(message)
            accepted_deletion_counter.restart()

        # release payments
        if datetime.now().hour == 0:
            perfect_ads = at_client.read_new_perfects()
            for ad in perfect_ads:
                chat_link = ad.get("Link")
                parsed_url = urlparse(chat_link)
                query_params = parse_qs(parsed_url.query)
                message_id = query_params.get('conversationId', [None])[0]
                message = ReleasePaymentMessage(message_id)
                # delete message id from cache
                msg_cache.delete(message_id)
                await server.send_message(message)


if __name__ == "__main__":
    asyncio.run(main())
