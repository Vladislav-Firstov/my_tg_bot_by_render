import os
import time
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from hydrogram import Client

# --- НАСТРОЙКИ ---
API_ID = int(os.environ.get("API_ID", 34011559))
API_HASH = os.environ.get("API_HASH", "8f89b19e09421936a9516fe549d9bd47")
CHAT_ID = int(os.environ.get("CHAT_ID", -1002391382566))
PORT = int(os.environ.get("PORT", 8080)) # Порт для Render
# ------------------

# Костыль для работы асинхронности Hydrogram в главном потоке
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

COMMANDS = [
    "/vino@vinoupbot",
    "/beer@upbeerbot",
    "/sisi@sisiupbot"
]

# Создаем клиент без автоматического старта
app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

async def send_all_commands():
    # Каждый час подключаемся заново
    await app.start()
    try:
        await app.resolve_peer(CHAT_ID)
        for cmd in COMMANDS:
            await app.send_message(CHAT_ID, cmd)
            print(f"Команда {cmd} отправлена!")
            await asyncio.sleep(2)
        print(f"--- Все команды успешно отправлены в {time.strftime('%H:%M:%S')}! ---")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
    finally:
        # ОБЯЗАТЕЛЬНО отключаемся от серверов Telegram до следующего часа
        await app.stop()

def bot_worker():
    time.sleep(5)
    while True:
        try:
            loop.run_until_complete(send_all_commands())
        except Exception as e:
            print(f"Ошибка в цикле бота: {e}")
            
        print("Засыпаем ровно на 1 час (3600 секунд)...")
        time.sleep(3600)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    bot_worker()
