# fmt: off
from app.models.ad import Ad
from app.utils import setup_logging
setup_logging()

from app.models import Context

import asyncio
import logging
from datetime import datetime
# fmt: on


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
                with open("data/ctx.json", "r") as f:
                    ctx = Context.from_file(f)
            except FileNotFoundError:
                ctx = Context.new()


async def main(ctx: Context | None):
    from app.messages.outgoing import SendOfferMessage
    from app.exceptions import InvalidAdException
    from app.clients import KleinanzeigenClient

    if not ctx:
        ctx = Context.new()

    ka_client = ctx.ka_client
    tg_client = ctx.tg_client
    msg_cache = ctx.msg_cache
    server = ctx.server
    catalog = ctx.catalog

    MAX_OFFERS_PER_HOUR = 40

    ka_client.previous_ads = ctx.kl_prev_ads

    await server.start()
    logging.info(f"Server started at {server.public_address}")

    ctx.start_counters()

    while True:
        try:
            with open("data/ctx.json", "w") as f:
                ctx.save(f)

            msg_cache.refresh()

            if ctx.self_connect_counter.is_finished():
                try:
                    await server.self_connect()
                except TimeoutError:
                    logging.error("Unable to connect to server, restarting")
                    await server.stop()
                    await server.start()
                ctx.self_connect_counter.restart()

            if ctx.catalog_refresh_counter.is_finished():
                catalog.refresh()
                ctx.catalog_refresh_counter.restart()

            await asyncio.sleep(1)

            # Send new ads offers
            try:
                ads = ka_client.get_fritz_ads()
            except Exception as e:
                logging.info(f"Client disconnected: {e}", exc_info=True)
                previous_ads = ka_client.previous_ads
                ctx.ka_client = KleinanzeigenClient()
                ka_client = ctx.ka_client
                ka_client.previous_ads = previous_ads
                ads = ka_client.get_fritz_ads()

            for ad in ads:
                try:
                    ad = Ad(ad)
                    message = SendOfferMessage(ad)
                except InvalidAdException:
                    continue

                if ctx.offers_sent_count <= 50:
                    logging.info(f"Sending offer to {ad.uid}")
                    await server.send_message(message)
                    tg_client.send_ad_alert(ad)
                    ctx.offers_sent_count += 1
                else:
                    logging.info(f"Putting {ad.uid} in queue")
                    ctx.pending_msgs_queue.put(message)

            # Send pending offers
            while not ctx.pending_msgs_queue.empty() and ctx.offers_sent_count <= MAX_OFFERS_PER_HOUR:
                message = ctx.pending_msgs_queue.get()
                logging.info(f"Sending offer to {message.link} (from queue)")
                tg_client.send_ad_alert(ad)
                await server.send_message(message)
                ctx.offers_sent_count += 1

            # Reset offers sent counter
            if ctx.offers_reset_counter.is_finished():
                ctx.offers_sent_count = 0
                ctx.offers_reset_counter.restart()

        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)
            await asyncio.sleep(1)  # Delay to prevent rapid error cycling

if __name__ == "__main__":
    asyncio.run(main_loop())
