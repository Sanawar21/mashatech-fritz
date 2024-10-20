import requests

from ..base import ChatLinkMessage
from ...utils import KA_USER_ID, KA_USER_TOKEN


class DeleteOfferMessage(ChatLinkMessage):
    """Delete an offer message."""
    type_ = "deleteMsg"

    def __init__(self, message_id):
        super().__init__(message_id)

    def delete_chat(self):

        url = f"https://gateway.kleinanzeigen.de/messagebox/api/users/{KA_USER_ID}/conversations?ids={self.message_id}"

        payload = {}
        headers = {'Authorization': 'Bearer ' + KA_USER_TOKEN, }

        response = requests.request(
            "DELETE", url, headers=headers, data=payload)

        print(response.text)
