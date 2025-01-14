import asyncio
import argparse
import logging
from datetime import datetime


async def main_loop():
    while True:
        try:
            await main()
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}", exc_info=True)
            # Optionally, add a short delay before restarting to prevent rapid restart loops
            await asyncio.sleep(5)


async def main():
    from app.utils import get_chat_id_from_link, setup_logging
    setup_logging()  # prevents the overriden logging.basicConfig from being called

    from app.clients import KleinanzeigenClient, TelegramClient, AirtableClient
    from app.server import WebSocketServer
    from app.models import Catalog, State
    from app.cache import MessageIDCache
    from app.messages.outgoing import SendOfferMessage, CheckOfferStatusMessage, DeleteOfferMessage, ReleasePaymentMessage
    from app.exceptions import InvalidAdException

    parser = argparse.ArgumentParser(description='Process some flags.')
    parser.add_argument('--load-state', action='store_true',
                        help='Load state from file')
    args = parser.parse_args()

    if args.load_state:
        try:
            with open("data/state.json", "r") as f:
                state = State.from_file(f)
        except FileNotFoundError:
            state = State.new()
    else:
        state = State.new()

    ka_client = KleinanzeigenClient()
    ka_client.previous_ads = state.kl_prev_ads

    tg_client = TelegramClient()
    at_client = AirtableClient()
    msg_cache = MessageIDCache()
    server = WebSocketServer('localhost', 8765)
    catalog = Catalog()

    MAX_OFFERS_PER_HOUR = 40

    await server.start()
    logging.info(f"Server started at {server.public_address}")

    # Start counters
    state.start_counters()

    while True:
        try:
            with open("data/state.json", "w") as f:
                state.save(f)

            msg_cache.refresh()

            if state.catalog_refresh_counter.is_finished():
                catalog.refresh()
                state.catalog_refresh_counter.restart()

            await asyncio.sleep(1)

            # Send new ads offers
            try:
                ads = ka_client.get_fritz_ads()
            except Exception as e:
                logging.info(f"Client disconnected: {e}", exc_info=True)
                previous_ads = ka_client.previous_ads
                ka_client = KleinanzeigenClient()
                ka_client.previous_ads = previous_ads
                ads = ka_client.get_fritz_ads()

            for ad in ads:
                try:
                    message = SendOfferMessage(ad)
                except InvalidAdException:
                    continue

                if state.offers_sent_count <= 50:
                    logging.info(f"Sending offer to {ad.uid}")
                    await server.send_message(message)
                    tg_client.send_ad_alert(ad)
                    state.offers_sent_count += 1
                else:
                    logging.info(f"Putting {ad.uid} in queue")
                    state.pending_msgs_queue.put(message)

            # Send pending offers
            while not state.pending_msgs_queue.empty() and state.offers_sent_count <= MAX_OFFERS_PER_HOUR:
                message = state.pending_msgs_queue.get()
                logging.info(f"Sending offer to {message.link} (from queue)")
                tg_client.send_ad_alert(ad)
                await server.send_message(message)
                state.offers_sent_count += 1

            # Reset offers sent counter
            if state.offers_reset_counter.is_finished():
                state.offers_sent_count = 0
                state.offers_reset_counter.restart()

            # Check status of offers
            if state.status_check_counter.is_finished():
                cached_ids = msg_cache.read_n_day_old(2)
                for id_ in cached_ids:
                    if id_.status != "paid":
                        logging.info(
                            f"Sending status check message for {id_.message_id}")
                        message = CheckOfferStatusMessage(id_.message_id)
                        await server.send_message(message)
                state.status_check_counter.restart()

            # Deletion of pending offers
            if state.pending_deletion_counter.is_finished():
                pending_offers = msg_cache.read_n_day_old(2, "pending")
                for offer in pending_offers:
                    logging.info(
                        f"Sending delete offer message for {offer.ad_uid} (pending)")
                    message = DeleteOfferMessage(offer.message_id)
                    msg_cache.delete(offer.message_id)
                    await server.send_message(message)
                state.pending_deletion_counter.restart()

            # Deletion of accepted offers that are not paid
            if state.accepted_deletion_counter.is_finished():
                accepted_offers = msg_cache.read_n_day_old(1, "accepted")
                for offer in accepted_offers:
                    logging.info(
                        f"Sending delete offer message for {offer.ad_uid} (accepted)")
                    message = DeleteOfferMessage(offer.message_id)
                    msg_cache.delete(offer.message_id)
                    await server.send_message(message)
                state.accepted_deletion_counter.restart()

            # Release payments
            if datetime.now().hour == 0:
                perfect_entries = at_client.read_new_perfects()
                for entry in perfect_entries:
                    logging.info(f"Releasing payment for {entry.ad_uid}")
                    message_id = get_chat_id_from_link(entry.chat_link)
                    message = ReleasePaymentMessage(message_id)
                    await server.send_message(message)

        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
            await asyncio.sleep(1)  # Delay to prevent rapid error cycling

if __name__ == "__main__":
    asyncio.run(main_loop())
