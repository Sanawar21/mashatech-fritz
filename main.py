import asyncio
import aiofiles
import logging
from datetime import datetime
from app.models import Context


async def main_loop():
    ctx = None
    while True:
        try:
            await main(ctx)
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}", exc_info=True)
            # Optionally, add a short delay before restarting to prevent rapid restart loops
            await asyncio.sleep(5)

            try:
                async with aiofiles.open("data/context.json", "w") as f:
                    text = await f.read()
                    ctx = Context.from_dict(eval(text))
            except FileNotFoundError:
                ctx = Context.new()


async def main(ctx: Context | None):
    from app.utils import get_chat_id_from_link, setup_logging
    setup_logging()  # prevents the overriden logging.basicConfig from being called

    from app.clients import KleinanzeigenClient, TelegramClient, AirtableClient
    from app.server import WebSocketServer
    from app.models import Catalog
    from app.cache import MessageIDCache
    from app.messages.outgoing import SendOfferMessage, CheckOfferStatusMessage, DeleteOfferMessage, ReleasePaymentMessage
    from app.exceptions import InvalidAdException

    ka_client = KleinanzeigenClient()
    tg_client = TelegramClient()
    at_client = AirtableClient()
    msg_cache = MessageIDCache()

    server = WebSocketServer('0.0.0.0', 8765)
    catalog = Catalog()

    MAX_OFFERS_PER_HOUR = 40

    if not ctx:
        context = Context.new()
    else:
        context = ctx

    ka_client.previous_ads = context.kl_prev_ads

    await server.start()
    logging.info(f"Server started at {server.public_address}")

    context.start_counters()

    while True:
        try:
            async with aiofiles.open("data/context.json", "w") as f:
                await f.write(context.to_json())

            msg_cache.refresh()

            if context.self_connect_counter.is_finished():
                try:
                    await server.self_connect()
                except TimeoutError:
                    logging.error("Unable to connect to server, restarting")
                    await server.stop()
                    await server.start()
                context.self_connect_counter.restart()

            if context.catalog_refresh_counter.is_finished():
                catalog.refresh()
                context.catalog_refresh_counter.restart()

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

                if context.offers_sent_count <= 50:
                    logging.info(f"Sending offer to {ad.uid}")
                    await server.send_message(message)
                    tg_client.send_ad_alert(ad)
                    context.offers_sent_count += 1
                else:
                    logging.info(f"Putting {ad.uid} in queue")
                    context.pending_msgs_queue.put(message)

            # Send pending offers
            while not context.pending_msgs_queue.empty() and context.offers_sent_count <= MAX_OFFERS_PER_HOUR:
                message = context.pending_msgs_queue.get()
                logging.info(f"Sending offer to {message.link} (from queue)")
                tg_client.send_ad_alert(ad)
                await server.send_message(message)
                context.offers_sent_count += 1

            # Reset offers sent counter
            if context.offers_reset_counter.is_finished():
                context.offers_sent_count = 0
                context.offers_reset_counter.restart()

            # Check status of offers
            if context.status_check_counter.is_finished():
                cached_ids = msg_cache.read_n_day_old(2)
                for id_ in cached_ids:
                    if id_.status != "paid":
                        logging.info(
                            f"Sending status check message for {id_.message_id}")
                        message = CheckOfferStatusMessage(id_.message_id)
                        await server.send_message(message)
                context.status_check_counter.restart()

            # Deletion of pending offers
            if context.pending_deletion_counter.is_finished():
                pending_offers = msg_cache.read_n_day_old(2, "pending")
                for offer in pending_offers:
                    logging.info(
                        f"Sending delete offer message for {offer.ad_uid} (pending)")
                    message = DeleteOfferMessage(offer.message_id)
                    msg_cache.delete(offer.message_id)
                    await server.send_message(message)
                context.pending_deletion_counter.restart()

            # Deletion of accepted offers that are not paid
            if context.accepted_deletion_counter.is_finished():
                accepted_offers = msg_cache.read_n_day_old(1, "accepted")
                for offer in accepted_offers:
                    logging.info(
                        f"Sending delete offer message for {offer.ad_uid} (accepted)")
                    message = DeleteOfferMessage(offer.message_id)
                    msg_cache.delete(offer.message_id)
                    await server.send_message(message)
                context.accepted_deletion_counter.restart()

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
