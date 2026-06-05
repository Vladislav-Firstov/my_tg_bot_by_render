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

# Безопасное получение порта для Render
try:
    PORT = int(os.environ.get("PORT", 8080))
except (ValueError, TypeError):
    PORT = 8080
# ------------------

# Инициализируем loop для главного потока
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

COMMANDS = [
    "/sisi@sisiupbot"
]

# 1. Класс-обработчик запросов для веб-сервера
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    
    def log_message(self, format, *args):
        return  # Отключаем лишний спам логов в консоль

# 2. Сама функция запуска веб-сервера (которая потерялась)
def run_web_server():
    try:
        server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
        print(f"Веб-сервер успешно запущен на порту {PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Ошибка веб-сервера: {e}")

# 3. Асинхронная функция отправки сообщений (с ежечасным переподключением)
async def send_all_commands():
    print("Устанавливаем свежее подключение к Telegram...")
    await app.start()
    try:
        await app.resolve_peer(CHAT_ID)
        for cmd in COMMANDS:
            await app.send_message(CHAT_ID, cmd)
            print(f"Команда {cmd} отправлена!")
            await asyncio.sleep(2)
        print(f"--- Все команды успешно отправлены в {time.strftime('%H:%M:%S')}! ---")
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")
    finally:
        # Отключаемся, чтобы сессия не зависала при смене IP сервера
        await app.stop()
        print("Сессия закрыта до следующего часа.")

# 4. Основной рабочий цикл бота
def bot_worker():
    # Даем веб-серверу 5 секунд на старт
    time.sleep(5)
    
    while True:
        try:
            loop.run_until_complete(send_all_commands())
        except Exception as e:
            print(f"Ошибка в основном цикле бота: {e}")
            
        print("Засыпаем ровно на 1 час (3600 секунд)...")
        time.sleep(3600)

if __name__ == "__main__":
    # Запускаем веб-сервер в фоновом потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Запускаем бота в главном потоке
    bot_worker()
