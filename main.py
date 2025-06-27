import time
import threading
import schedule 
from bot_telegram import TelegramBot
from firebase_connector import FirebaseConnector
import requests
from fuzzy_mamdani import FuzzyMamdani


BOT_TOKEN = "8158211888:AAFC35N85-7QsspxvorzZb75eWD4AwKe8nE"
CHAT_ID = 1099636525
FIREBASE_CRED_PATH = 'greenhouse.json'
FIREBASE_DATABASE_URL = 'https://kondisigreenhouse-default-rtdb.asia-southeast1.firebasedatabase.app/'

try:
    firebase_connector = FirebaseConnector(FIREBASE_CRED_PATH, FIREBASE_DATABASE_URL)
    telegram_bot = TelegramBot(BOT_TOKEN, CHAT_ID)
    fuzzy_mamdani = FuzzyMamdani(FIREBASE_CRED_PATH, FIREBASE_DATABASE_URL, BOT_TOKEN, CHAT_ID)
except Exception as e:
    print(f"[{time.strftime('%H:%M:%S')}] Gagal melakukan inisialisasi awal: {e}")
    exit() 

running = False 

def send_report():
    print(f"[{time.strftime('%H:%M:%S')}] Menjalankan tugas terjadwal: send_report...")
    try:
        data = firebase_connector.get_data('sensor')
        if data:
            suhu_air = data.get('suhu_air', 'Data tidak tersedia')
            ph_air = data.get('ph_air', 'Data tidak tersedia')
            cahaya = data.get('cahaya', 'Data tidak tersedia')
            co2 = data.get('co2', 'Data tidak tersedia')
            suhu_air_val = data.get('suhu_air', 0)
            ph_air_val = data.get('ph_air', 0)
            cahaya_val = data.get('cahaya', 0)
            co2_val = data.get('co2', 0)

            suhu_air_label = fuzzy_mamdani.get_linguistic_label(fuzzy_mamdani.suhu_air, suhu_air_val)
            ph_air_label = fuzzy_mamdani.get_linguistic_label(fuzzy_mamdani.ph_air, ph_air_val)
            cahaya_label = fuzzy_mamdani.get_linguistic_label(fuzzy_mamdani.cahaya, cahaya_val)
            co2_label = fuzzy_mamdani.get_linguistic_label(fuzzy_mamdani.co2, co2_val)

            kondisi = fuzzy_mamdani.calculate_fuzzy()

            if kondisi is not None:
                kondisi_linguistik = fuzzy_mamdani.get_linguistic_condition(kondisi)

                message = (f"KONDISI GREENHOUSE🌳\n"
                           f"=====================\n"
                           f"📅Tanggal : {time.strftime('%d-%m-%Y')}\n" 
                           f"⏱️Jam     : {time.strftime('%H:%M')}\n"
                           f"🌡️Suhu Air  : {suhu_air} °C ({suhu_air_label})\n"
                           f"💧pH Air    : {ph_air} ({ph_air_label})\n"
                           f"💡Cahaya    : {cahaya} % ({cahaya_label})\n"
                           f"🍃CO2       : {co2} ppm ({co2_label})\n"
                           f"=====================\n"
                           f"🧠Nilai Fuzzy: {kondisi:.2f}\n"
                           f"📊Kondisi : {kondisi_linguistik}")

                telegram_bot.send_message(message)
            else:
                telegram_bot.send_message("⚠️ Data fuzzy tidak dapat dihitung.")
        else:
            telegram_bot.send_message("⚠️ Data sensor tidak ditemukan di Firebase, kemungkinan sensor mati atau ada masalah koneksi dengan Firebase.")
            
    except requests.exceptions.ConnectionError as e:
        print(f"[{time.strftime('%H:%M:%S')}] Gagal terhubung ke Firebase: {e}")
        telegram_bot.send_message("❌ Gagal mengambil data. Tidak dapat terhubung ke server Firebase.")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Error di send_report: {e}")
        telegram_bot.send_message(f"⚠️ Terjadi kesalahan internal saat membuat laporan: {e}")

def scheduler_loop():
    global running
    while running:
        schedule.run_pending()
        time.sleep(1) 

def listen_messages():
    global running
    last_update_id = None
    print("Bot Telegram sedang mendengarkan perintah...")
    telegram_bot.send_keyboard()
    
    while True:
        try:
            resp = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates', params={'offset': last_update_id, 'timeout': 10})
            resp.raise_for_status()  # Akan raise error jika status code bukan 2xx
            data = resp.json()

            for result in data.get('result', []):
                last_update_id = result['update_id'] + 1
                if 'message' in result:
                    text = result['message'].get('text', '').strip()
                    
                    if text == "▶️ Start":
                        if not running:
                            running = True
                            
                            jadwal_jam = ["07:00", "09:00", "11:00", "13:00", "15:00", "17:00"]
                            for jam in jadwal_jam:
                                schedule.every().day.at(jam).do(send_report)

                            telegram_bot.send_message(f"✅ Bot mulai berjalan. Laporan akan dikirim pada jam: {', '.join(jadwal_jam)}.")
                            
                            threading.Thread(target=scheduler_loop, daemon=True).start()
                        else:
                            telegram_bot.send_message("⚠️ Bot sudah berjalan.")
                            
                    elif text == "🪴Status":
                        send_report()
                        
                    elif text == "⏹ Stop":
                        if running:
                            running = False
                            schedule.clear()  
                            telegram_bot.send_message("🛑 Pengiriman dihentikan dan semua jadwal dihapus.")
                        else:
                            telegram_bot.send_message("⚠️ Bot sudah dalam keadaan berhenti.")

        
        except requests.exceptions.ConnectionError as e:
            print(f"[{time.strftime('%H:%M:%S')}] Gagal terhubung ke API Telegram: {e}. Mencoba lagi dalam 10 detik...")
            time.sleep(10)
            
        except requests.exceptions.RequestException as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error saat request ke Telegram: {e}")
            time.sleep(5)

        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error tidak terduga di listen_messages: {e}")
            time.sleep(5)

if __name__ == "__main__":
    listen_messages()