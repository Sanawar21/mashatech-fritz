from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_AD_ALERT_CHAT_ID = os.getenv("TG_AD_ALERT_CHAT_ID")
TG_OFFER_ACCEPTED_CHAT_ID = os.getenv("TG_OFFER_ACCEPTED_CHAT_ID")
TG_AMOUNT_PAID_CHAT_ID = os.getenv("TG_AMOUNT_PAID_CHAT_ID")
TG_API_ENDPOINT = f"https://api.telegram.org/bot{TG_BOT_TOKEN}"

KA_USERNAME = os.getenv("KA_USERNAME")
KA_PASSWORD = os.getenv("KA_PASSWORD")

AT_API_KEY = os.getenv("AT_API_KEY")
AT_BASE_ID = os.getenv("AT_BASE_ID")
AT_TABLE_NAME = os.getenv("AT_TABLE_NAME")

CATALOG = {
    "510": 20,
    "520": 10,
    "530": 15,
    "540": 30,
    "546": 38,
    "1000": 15,
    "1220": 20,
    "1240": 35,
    "1260": 40,
    "100": 25,
    "200": 15,
    "310": 15,
    "450": 25,
    "600": 5,
    "1160": 30,
    "1200": 35,
    "1750": 38,
    "2400": 40,
    "3000": 65,
    "6000": 90,
    "3490": 5,
    "4020": 18,
    "4040": 25,
    "7390": 5,
    "7430": 5,
    "7490": 20,
    "7530": 45,
    "7530 ax": 70,
    "7590": 90,
    "7590 ax": 100,
    "6660": 90,
    "6590": 50,
    "6591": 90,
    "6820": 55,
    "5590": 110,
}

MESSAGES = {
    "universal": """Guten Tag,
Wenn das Gerät einwandfrei funktioniert, bitte ich Sie, meinen Preisvorschlag anzunehmen. Die Zahlung werde ich umgehend über die Kleinanzeigen-Bezahlfunktion veranlassen.
Mit freundlichen Grüßen,
Naveed
    """,
    "4020": """Guten Tag,
sofern die Fritzbox 4020 einwandfrei funktioniert und die Artikelnummer 20002713 (auf der Rückseite des Geräts angegeben) zutrifft, bitte ich Sie, meinen Preisvorschlag anzunehmen. Die Zahlung werde ich umgehend über die Kleinanzeigen-Bezahlfunktion veranlassen.
Mit freundlichen Grüßen,
Naveed""",
    "4040": """Guten Tag, falls die Fritzbox 4040 voll funktionsfähig ist und die Artikelnummer 20002763 (auf der Rückseite des Geräts angegeben) korrekt ist, wäre ich Ihnen dankbar, wenn Sie meinen Preisvorschlag akzeptieren. Ich werde die Zahlung sofort über die Kleinanzeigen-Bezahlfunktion durchführen. Mit freundlichen Grüßen, Naveed
    """,
    "7490": """Guten Tag, vorausgesetzt, die Fritzbox 7490 ist in einwandfreiem Zustand und die Artikelnummer 20002584 (auf der Rückseite des Geräts angegeben) stimmt, bitte ich Sie, meinen Preisvorschlag zu akzeptieren. Die Zahlung werde ich direkt im Anschluss über die Kleinanzeigen-Bezahlfunktion abwickeln. Mit freundlichen Grüßen, Naveed
    """,
    "7530": """Guten Tag, sofern die Fritzbox 7530 ordnungsgemäß funktioniert und die Artikelnummer 20002839 (auf der Rückseite des Geräts angegeben) korrekt ist, bitte ich um Annahme meines Preisvorschlags. Die Zahlung werde ich unverzüglich über die Kleinanzeigen-Bezahlfunktion tätigen.Mit freundlichen Grüßen,Naveed
    """,
    "7530 ax": """Guten Tag, falls die FritzBox 7530 ax voll funktionsfähig ist und die Artikelnummer 20002930 (auf der Rückseite des Geräts angegeben) zutrifft, bitte ich Sie, meinen Preisvorschlag zu akzeptieren. Die Zahlung werde ich unmittelbar über die Kleinanzeigen-Bezahlfunktion vornehmen. Mit freundlichen Grüßen, Naveed
    """,
    "7590": """Guten Tag, vorausgesetzt, die Fritzbox 7590 ist funktionstüchtig und die Artikelnummer 20002784 (auf der Rückseite des Geräts angegeben) stimmt, wäre ich Ihnen verbunden, wenn Sie meinen Preisvorschlag annehmen. Die Zahlung werde ich sofort über die Kleinanzeigen-Bezahlfunktion veranlassen. Mit freundlichen Grüßen, Naveed
    """,
    "7590 ax": """Guten Tag, falls die Fritzbox 7590 ax ordnungsgemäß funktioniert und die Artikelnummer 20002998 (auf der Rückseite des Geräts angegeben) korrekt ist, bitte ich um Annahme meines Preisvorschlags. Die Zahlung werde ich unverzüglich über die Kleinanzeigen-Bezahlfunktion abwickeln. Mit freundlichen Grüßen, Naveed
    """,
    "6660": """Guten Tag, sofern die Fritzbox 6660 einwandfrei arbeitet und die Artikelnummer 20002910 (auf der Rückseite des Geräts angegeben) zutreffend ist, bitte ich um die Annahme meines Preisvorschlags. Die Zahlung werde ich unmittelbar über die Kleinanzeigen-Bezahlfunktion tätigen. Mit freundlichen Grüßen, Naveed
    """,
    "6590": """Guten Tag, falls die Fritzbox 6590 in einwandfreiem Zustand ist und die Artikelnummer 20002781 (auf der Rückseite des Geräts angegeben) korrekt ist, würde ich mich freuen, wenn Sie meinen Preisvorschlag akzeptieren. Die Zahlung erfolgt dann umgehend über die Kleinanzeigen-Bezahlfunktion. Mit freundlichen Grüßen, Naveed
    """,
    "6591": """Guten Tag, sofern die Fritzbox 6591 voll funktionsfähig ist und die Artikelnummer 20002857 (auf der Rückseite des Geräts angegeben) übereinstimmt, bitte ich um Annahme meines Preisvorschlags. Die Zahlung werde ich direkt über die Kleinanzeigen-Bezahlfunktion veranlassen. Mit freundlichen Grüßen, Naveed
    """,
    "5590": """Guten Tag,

sofern die Fritzbox 5590 voll funktionsfähig ist und die Artikelnummer 20002981 (auf der Rückseite des Geräts angegeben) übereinstimmt, bitte ich um Annahme meines Preisvorschlags. Die Zahlung werde ich direkt über die Kleinanzeigen-Bezahlfunktion veranlassen.
Mit freundlichen Grüßen,
Naveed
    """,
}
