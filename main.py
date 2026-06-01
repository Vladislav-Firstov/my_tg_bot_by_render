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

# Простейший веб-сервер для обмана Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    
    def log_message(self, format, *args):
        return # Отключаем лишний спам логов сервера в консоль

def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    print(f"Веб-сервер запущен на порту {PORT}")
    server.serve_forever()

# Асинхронная функция отправки сообщений
async def send_all_commands():
    async with app:
        try:
            await app.resolve_peer(CHAT_ID)
            for cmd in COMMANDS:
                await app.send_message(CHAT_ID, cmd)
                print(f"Команда {cmd} отправлена!")
                await asyncio.sleep(2)
            print(f"--- Все команды успешно отправлены в {time.strftime('%H:%M:%S')}! ---")
        except Exception as e:
            print(f"Ошибка при отправке: {e}")

# Основной рабочий цикл бота
def bot_worker():
    # Даем веб-серверу 5 секунд на старт, чтобы Render зафиксировал успешный запуск
    time.sleep(5)
    
    while True:
        try:
            # Запускаем отправку
            loop.run_until_complete(send_all_commands())
        except Exception as e:
            print(f"Ошибка в цикле бота: {e}")
            
        print("Засыпаем ровно на 1 час (3600 секунд)...")
        time.sleep(3600) # Железный интервал в 1 час

if __name__ == "__main__":
    # 1. Запускаем веб-сервер в фоновом потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # 2. Запускаем основной бесконечный цикл бота в главном потоке
    bot_worker()
