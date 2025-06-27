import requests
import firebase_admin
class TelegramBot:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}'

    def send_message(self, text):
        # Mengirim pesan ke chat Telegram.
        requests.post(f"{self.base_url}/sendMessage", data={'chat_id': self.chat_id, 'text': text})

    def send_keyboard(self):
        # Mengirim pesan dengan tombol keyboard untuk kontrol bot.
        keyboard = {
            "keyboard": [
                ["▶️ Start", "🪴Status","⏹ Stop"]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        data = {
            "chat_id": self.chat_id,
            "text": "Gunakan tombol di bawah untuk mengontrol bot: \n▶️Start = Memulai pengiriman laporan otomatis \n🪴Status = Mengirim laporan Saat ini \n⏹Stop = Menghentikan pengiriman laporan otomatis",
            "reply_markup": keyboard 
        }
        requests.post(f"{self.base_url}/sendMessage", json=data)
