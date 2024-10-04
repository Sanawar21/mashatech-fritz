from ..utils import TG_API_ENDPOINT, TG_AMOUNT_PAID_CHAT_ID, TG_AD_ALERT_CHAT_ID, TG_OFFER_ACCEPTED_CHAT_ID
from ..models import Ad

import requests
import datetime
import pytz
import logging


class TelegramClient:

    def __get_current_date(self):
        """Returns current german time in the format: 1st January, 2021. Friday 12:00:00"""
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        german_timezone = pytz.timezone("Europe/Berlin")
        german_time = utc_now.astimezone(german_timezone)

        def get_day_suffix(day):
            if 4 <= day <= 20 or 24 <= day <= 30:
                return "th"
            else:
                return ["st", "nd", "rd"][day % 10 - 1]

        formatted_date_time = german_time.strftime(
            f"%-d{get_day_suffix(german_time.day)} %B, %Y. %A %H:%M:%S"
        )

        if formatted_date_time.startswith('0'):
            formatted_date_time = german_time.strftime(
                f"%#d{get_day_suffix(german_time.day)} %B, %Y. %A %H:%M:%S"
            )

        return formatted_date_time

    def send_message(self, text, chat_id):
        """
        set `chat_id` from one of the telegram chat ids in utils.
        """

        url = f"{TG_API_ENDPOINT}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        requests.get(url, params=params)

    def send_ad_alert(self, ad: Ad):
        text_lines = [
            f"Title: {ad.title}",
            "Products:",
            "\n".join(
                [f"    {match.quantity}x {match.product} ({match.price} € each)" for match in ad.matches]),
            f"Calculated Price: {sum([match.price for match in ad.matches])} €",
            f"Offered Price: {int(ad.offer_price)} €",
            f"Listed Price: {int(ad.price)} €",
            f"Link: {ad.link}"
        ]
        text = "\n".join(text_lines)
        logging.info("Sending message to Telegram (Ad alert)")
        self.send_message(text, TG_AD_ALERT_CHAT_ID)

    def send_offer_accepted_alert(self, ad: Ad, price: float, ad_chat_link: str):
        text_lines = [
            f"Title: {ad.title}",
            "Products:",
            "\n".join(
                [f"    {match.quantity}x {match.product} ({match.price} € each)" for match in ad.matches]),
            f"Amount To Pay: {int(price)} €",
            f"Chat Link: {ad_chat_link}"
        ]
        text = "\n".join(text_lines)
        logging.info("Sending message to Telegram (Offer accepted)")
        self.send_message(text, TG_OFFER_ACCEPTED_CHAT_ID)

    def send_amount_paid_alert(self, ad: Ad, ad_chat_link: str):
        text_lines = [
            f"Title: {ad.title}",
            f"Poster: {ad.poster_name}",
            f"Date: {self.__get_current_date()}",
            f"Postal code: {ad.zip_code}",
            "Products:",
            "\n".join(
                [f"    {match.quantity}x {match.product} ({match.price} € each)" for match in ad.matches]),
            f"Amount Paid: {int(ad.offer_price)} €",
            f"Chat Link: {ad_chat_link}"
        ]
        text = "\n".join(text_lines)
        logging.info("Sending message to Telegram (Amount paid)")
        self.send_message(text, TG_AMOUNT_PAID_CHAT_ID)


if __name__ == '__main__':
    TelegramClient().listen_and_run()
