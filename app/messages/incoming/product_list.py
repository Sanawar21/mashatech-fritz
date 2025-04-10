from ..base import IncomingMessage
from ...utils import get_ad_id_from_link
from ...models import Context


class ProductListMessage(IncomingMessage):
    """""Standard incoming product list message. Edit the airtable row
    and add the new products in it. This message is sent when the extension
    detects that the user has manually typed the purchased products in the chat."""

    type_ = "productListDetected"

    def __init__(self, chat_link: str, text: str) -> None:
        self.chat_link = chat_link
        self.text = text
        self.ad_uid = get_ad_id_from_link(self.chat_link)
        super().__init__()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data.get('chat_link'),
            data.get('text')
        )

    def process(self, ctx: Context):
        ctx.at_client.update(self.ad_uid, "Products", self.text)
