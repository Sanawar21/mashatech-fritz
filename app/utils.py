from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import os

load_dotenv()


def get_ad_id_from_link(link: str) -> str:
    return link.split("/")[-1].split("-")[0]


def get_chat_id_from_link(link: str) -> str:
    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('conversationId', [None])[0]


def setup_logging():
    import logging
    import sys
    import os
    import time

    # create logs directory if not exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/output-{int(time.time())}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Function to handle uncaught exceptions

    def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow keyboard interrupts to pass through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.error("Uncaught Exception", exc_info=(
            exc_type, exc_value, exc_traceback))

    # Set the custom exception hook
    sys.excepthook = log_uncaught_exceptions


# Load environment variables
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_AD_ALERT_CHAT_ID = os.getenv("TG_AD_ALERT_CHAT_ID")
TG_OFFER_ACCEPTED_CHAT_ID = os.getenv("TG_OFFER_ACCEPTED_CHAT_ID")
TG_AMOUNT_PAID_CHAT_ID = os.getenv("TG_AMOUNT_PAID_CHAT_ID")
TG_API_ENDPOINT = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

KA_USERNAME = os.getenv("KA_USERNAME")
KA_PASSWORD = os.getenv("KA_PASSWORD")
KA_USER_ID = os.getenv("KA_USER_ID")
KA_USER_TOKEN = os.getenv("KA_USER_TOKEN")

AT_API_KEY = os.getenv("AT_API_KEY")
AT_BASE_ID = os.getenv("AT_BASE_ID")
AT_TABLE_NAME = os.getenv("AT_TABLE_NAME")
AT_CATALOG_NAME = os.getenv("AT_CATALOG_NAME")

CATALOG = {
    "510": 5,
    "520": 10,
    "530": 15,
    "540": 20,
    "546": 38,
    "1000": 15,
    "1220": 20,
    "1240": 30,
    "1260": 45,
    "100": 5,
    "200": 5,
    "310": 15,
    "450": 25,
    "600": 5,
    "1160": 30,
    "1200": 30,
    "1750": 38,
    "2400": 40,
    "3000": 70,
    "6000": 90,
    "3490": 1,
    "4020": 18,
    "4040": 25,
    "7390": 1,
    "7430": 1,
    "7490": 20,
    "7530": 45,
    "7530 ax": 70,
    "7590": 80,
    "7590 ax": 90,
    "6660": 90,
    "6590": 70,
    "6591": 70,
    "6820": 52,
    "5590": 110,
}

MESSAGES = {
    "universal": """Guten Tag,
wenn das Gerät einwandfrei funktioniert, würde ich mich freuen, wenn Sie meinen Preisvorschlag annehmen. Ich werde die Zahlung umgehend über die Kleinanzeigen-Bezahlfunktion veranlassen.
Mit freundlichen Grüßen,
Naveed
    """,
    "4020": """Guten Tag, falls die Fritzbox 4020 einwandfrei funktioniert und die Artikelnummer 20002713 übereinstimmt, würde ich mich freuen, wenn Sie meinen Preisvorschlag annehmen. Bitte prüfen Sie, dass die Artikelnummer auf der Rückseite des Geräts steht und wirklich passt. Ich kann die Zahlung direkt über Kleinanzeigen abwickeln.
Viele Grüße,
Naveed
""",
    "4040": """Guten Tag, wenn die Fritzbox 4040 voll funktionsfähig ist und die Artikelnummer 20002763 korrekt ist, freue ich mich über die Annahme meines Angebots. Die Artikelnummer ist wichtig und sollte auf der Rückseite des Geräts stehen – bitte nur annehmen, wenn diese wirklich passt. Die Zahlung erfolgt sofort über Kleinanzeigen.
Mit freundlichen Grüßen,
Naveed
    """,
    "7490": """Guten Tag, sofern die Fritzbox 7490 gut funktioniert und die Artikelnummer 20002584 stimmt, wäre ich interessiert, wenn Sie meinen Preisvorschlag akzeptieren. Die Artikelnummer sollte auf der Rückseite des Geräts angegeben sein und exakt übereinstimmen. Die Zahlung erfolgt über Kleinanzeigen.
Beste Grüße,
Naveed
    """,
    "7530": """Guten Tag, wenn die Fritzbox 7530 in Ordnung ist und die Artikelnummer 20002839 übereinstimmt, würde ich mich freuen, wenn Sie mein Angebot annehmen. Bitte prüfen Sie, dass die Artikelnummer auf der Rückseite steht und genau passt. Die Zahlung kann direkt über Kleinanzeigen abgewickelt werden.
Viele Grüße,
Naveed
    """,
    "7530 ax": """Guten Tag, falls die FritzBox 7530 ax voll funktionstüchtig ist und die Artikelnummer 20002930 korrekt ist, freue ich mich über die Annahme meines Preisvorschlags. Die Artikelnummer sollte auf der Rückseite des Geräts stehen und unbedingt übereinstimmen. Die Zahlung erfolgt unverzüglich über Kleinanzeigen.
Beste Grüße,
Naveed
    """,
    "7590": """Guten Tag, sofern die Fritzbox 7590 funktioniert und die Artikelnummer 20002784 korrekt ist, freue ich mich, wenn Sie mein Angebot akzeptieren. Die Artikelnummer ist wichtig und befindet sich auf der Rückseite des Geräts – bitte nur annehmen, wenn sie stimmt. Die Zahlung erfolgt über Kleinanzeigen.
Mit freundlichen Grüßen,
Naveed
    """,
    "7590 ax": """Guten Tag, falls die Fritzbox 7590 ax einwandfrei funktioniert und die Artikelnummer 20002998 übereinstimmt, wäre ich an einem Kauf interessiert. Bitte prüfen Sie, dass die Artikelnummer auf der Rückseite des Geräts steht und wirklich passt. Ich werde die Zahlung direkt über Kleinanzeigen abwickeln.
Grüße,
Naveed
    """,
    "6660": """Guten Tag, wenn die Fritzbox 6660 in Ordnung ist und die Artikelnummer 20002910 korrekt ist, freue ich mich über die Annahme meines Preisvorschlags. Die Artikelnummer sollte auf der Rückseite des Geräts stehen und unbedingt stimmen. Die Zahlung erfolgt über Kleinanzeigen.
Beste Grüße,
Naveed
    """,
    "6590": """Guten Tag, sofern die Fritzbox 6590 einwandfrei funktioniert und die Artikelnummer 20002781 übereinstimmt, freue ich mich, wenn Sie mein Angebot annehmen. Wichtig: Die Artikelnummer steht auf der Rückseite des Geräts – bitte nur annehmen, wenn sie exakt stimmt. Die Zahlung wird direkt über Kleinanzeigen abgewickelt.
Viele Grüße,
Naveed
    """,
    "6591": """Guten Tag, falls die Fritzbox 6591 voll funktionsfähig ist und die Artikelnummer 20002857 korrekt ist, freue ich mich über die Annahme meines Angebots. Die Artikelnummer ist sehr wichtig und sollte auf der Rückseite des Geräts stehen – bitte nur akzeptieren, wenn sie wirklich stimmt. Die Zahlung erfolgt sofort über Kleinanzeigen.
Beste Grüße,
Naveed
    """,
    "5590": """Guten Tag, wenn die Fritzbox 5590 in gutem Zustand ist und die Artikelnummer 20002981 übereinstimmt, freue ich mich, wenn Sie meinen Preisvorschlag annehmen. Bitte prüfen Sie unbedingt, dass die Artikelnummer exakt passt und sich auf der Rückseite befindet. Die Zahlung erfolgt direkt über Kleinanzeigen.
Grüße,
Naveed
    """,
}
