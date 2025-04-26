# from app.models.ad import AdParser
# from app.messages.outgoing import SendOfferMessage
# from app.models import Catalog
# from app.utils import GEMINI_SYSTEM_INSTRUCTIONS_PATH

import deep_translator

product_title = "Hallo"
product_description = "Dies ist eine Produktbeschreibung"

translator = deep_translator.GoogleTranslator(
    source="de", target="en")
title = translator.translate(product_title)
description = translator.translate(product_description)

print(f"Title: {title}")
print(f"Description: {description}")
