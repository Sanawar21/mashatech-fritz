from app.models.ad import AdParser
from app.messages.outgoing import SendOfferMessage

AdParser.update_catalog()
SendOfferMessage.update_messages_list()
