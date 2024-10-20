import asyncio
import queue
import logging

from datetime import datetime


async def main():
    from app.utils import get_chat_id_from_link, setup_logging
    setup_logging()  # prevents the overriden logging.basicConfig from being called

    from app.clients import KleinanzeigenClient, TelegramClient, AirtableClient
    from app.server import WebSocketServer
    from app.models import Counter, Catalog
    from app.cache import MessageIDCache
    from app.messages.outgoing import SendOfferMessage, CheckOfferStatusMessage, DeleteOfferMessage, ReleasePaymentMessage
    from app.exceptions import InvalidAdException

    ka_client = KleinanzeigenClient()
    tg_client = TelegramClient()
    at_client = AirtableClient()
    msg_cache = MessageIDCache()
    server = WebSocketServer('0.0.0.0', 8765)
    catalog = Catalog()

    pending_msgs_queue = queue.Queue()  # Contains SendOfferMessage s
    offers_sent = 0

    # initialize counters
    status_check_counter = Counter(0, 5, 0)
    offers_reset_counter = Counter(1, 0, 0)
    pending_deletion_counter = Counter(48, 0, 0)
    accepted_deletion_counter = Counter(24, 0, 0)
    self_connect_counter = Counter(0, 5, 0)
    catalog_refresh_counter = Counter(0, 5, 0)

    await server.start()
    logging.info(f"Server started at {server.public_address}")

    # start counters
    offers_reset_counter.start()
    status_check_counter.start()
    pending_deletion_counter.start()
    accepted_deletion_counter.start()
    self_connect_counter.start()
    catalog_refresh_counter.start()

    while True:

        msg_cache.refresh()

        if self_connect_counter.is_finished():
            await server.self_connect()
            self_connect_counter.restart()

        if catalog_refresh_counter.is_finished():
            catalog.refresh()
            catalog_refresh_counter.restart()

        await asyncio.sleep(1)

        # send new add offers
        try:
            ads = ka_client.get_fritz_ads()
        except Exception as e:
            # The client has disconnected so create a new one
            logging.info(
                f"Client disconnected: {e}", exc_info=True)
            previous_ads = ka_client.previous_ads
            ka_client = KleinanzeigenClient()
            ka_client.previous_ads = previous_ads
            ads = ka_client.get_fritz_ads()

        for ad in ads:
            try:
                message = SendOfferMessage(ad)
            except InvalidAdException:
                continue

            if offers_sent <= 50:
                logging.info(f"Sending offer to {ad.uid}")
                await server.send_message(message)
                tg_client.send_ad_alert(ad)
                offers_sent += 1
            else:
                logging.info(f"Putting {ad.uid} in queue")
                pending_msgs_queue.put(message)

        # send pending offers
        while not pending_msgs_queue.empty() and offers_sent <= 50:
            message = pending_msgs_queue.get()
            logging.info(f"Sending offer to {message.link} (from queue)")
            tg_client.send_ad_alert(ad)
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
                    logging.info(
                        f"Sending status check message for {id_.message_id}")
                    message = CheckOfferStatusMessage(id_.message_id)
                    await server.send_message(message)
            status_check_counter.restart()

        # deletion of pending offers
        if pending_deletion_counter.is_finished():
            pending_offers = msg_cache.read_n_day_old(2, "pending")
            for offer in pending_offers:
                logging.info(
                    f"Sending delete offer message for {offer.ad_uid} (pending)")
                message = DeleteOfferMessage(offer.message_id)
                msg_cache.delete(offer.message_id)
                await server.send_message(message)
            pending_deletion_counter.restart()

        # deletion of accepted offers that are not paid
        if accepted_deletion_counter.is_finished():
            accepted_offers = msg_cache.read_n_day_old(1, "accepted")
            for offer in accepted_offers:
                logging.info(
                    f"Sending delete offer message for {offer.ad_uid} (accepted)")

                message = DeleteOfferMessage(offer.message_id)
                msg_cache.delete(offer.message_id)
                await server.send_message(message)
            accepted_deletion_counter.restart()

        # release payments
        if datetime.now().hour == 0:
            perfect_entries = at_client.read_new_perfects()
            for entry in perfect_entries:
                logging.info(f"Releasing payment for {entry.ad_uid}")
                message_id = get_chat_id_from_link(entry.chat_link)
                message = ReleasePaymentMessage(message_id)
                await server.send_message(message)

if __name__ == "__main__":
    asyncio.run(main())
