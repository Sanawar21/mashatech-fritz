import time
import requests
from ..utils import TG_API_ENDPOINT, TG_AMOUNT_PAID_CHAT_ID


class TelegramClient:

    @staticmethod
    def get_updates(offset=None):
        url = f"{TG_API_ENDPOINT}/getUpdates"
        params = {'timeout': 100, 'offset': offset}
        response = requests.get(url, params=params)
        return response.json()

    @staticmethod
    def send_message(text, chat_id):
        """
        set `to` from one of the chat ids in utils.Contants class.
        """

        url = f"{TG_API_ENDPOINT}/sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        requests.get(url, params=params)

    @staticmethod
    def send_excel_file(excel_file_path, chat_id=TG_AMOUNT_PAID_CHAT_ID):
        url = f"{TG_API_ENDPOINT}/sendDocument"
        files = {'document': open(excel_file_path, 'rb')}
        params = {'chat_id': chat_id}
        return requests.post(url, files=files, data=params)

    def listen_and_run(self):
        """
        listens for "sheet" in chats and sends the excel file where it finds them.
        """

        last_update_id = None

        while True:
            updates = self.get_updates(last_update_id)

            if 'result' in updates:
                for update in updates['result']:
                    last_update_id = update['update_id'] + 1
                    message = update.get('message')

                    if message:
                        chat_id = message['chat']['id']
                        text = message.get('text')

                        if text and text.lower() == 'sheet':
                            self.send_message(
                                'Sending the Excel file...', chat_id)
                            self.send_excel_file(chat_id)
                        else:
                            self.send_message(
                                'Send "sheet" to receive an Excel file.', chat_id)

            time.sleep(1)


if __name__ == '__main__':
    TelegramClient().listen_and_run()
