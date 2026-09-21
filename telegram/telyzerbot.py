import requests
from config import Config


class TelyzerBot:
    def __init__(self):
        self.cf = Config()
        self.base_url = f"https://api.telegram.org/bot{self.cf.telyzer_bot}/"
        self.session = requests.Session()

    def send_message(self, chat_id, message, timeout=10):
        url = self.base_url + "sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        try:
            response = self.session.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"ok": False, "error": str(e)}