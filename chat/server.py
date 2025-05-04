"""Chat Server"""

import socket
import threading
import logging
from datetime import datetime as dt
from os import makedirs as mkdir
from os.path import join

# Константы для сервера: адрес, порт и размер буфера
HOST = 'localhost'
PORT = 54321
BUFFER_SIZE = 1024

# Директория для логов
mkdir('logs', exist_ok=True)
logging.basicConfig(
    handlers=(
        logging.FileHandler(join('logs', f'chat-{dt.now().strftime("%Y-%m-%d_%H-%M")}.log')),
        logging.StreamHandler()
    ),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Хранение клиентов (имя -> сокет)
clients = {}

# Функция для отправки сообщения всем клиентам (с опцией уведомления отправителя)
def broadcast(sender, message, notify_sender=True):
    """
    Send a message to all clients except the sender (public chat).
    If notify_sender is True, send delivery confirmation to sender.

    Args:
        sender (str): Name of the sender.
        message (str): Message text.
        notify_sender (bool): Whether to notify the sender about delivery.
    """
    delivered = False
    # Рассылка сообщения всем клиентам, кроме отправителя
    for name, sock in clients.items():
        if name != sender:
            try:
                sock.sendall(f"{sender}: {message}".encode())
                delivered = True
            except Exception as e:
                logging.error(f"Error sending to {name}: {e}")
    # Уведомление отправителя о доставке
    if notify_sender and sender in clients:
        try:
            if delivered:
                clients[sender].sendall(b"Delivered to ALL")
                logging.info(f"{sender} -> ALL: {message}")
            else:
                clients[sender].sendall(b"No users to deliver to.")
        except Exception as e:
            logging.error(f"Error sending delivery confirmation to {sender}: {e}")

# Функция для отправки личного сообщения
def send_private(sender, recipient, message):
    """
    Send a private message to the recipient.

    Args:
        sender (str): Name of the sender.
        recipient (str): Name of the recipient.
        message (str): Message text.
    """
    # Проверка наличия получателя среди клиентов
    if recipient in clients:
        try:
            if sender == recipient:
                clients[sender].sendall(b"Cannot send private messages to yourself.")
                logging.warning(f"{sender} tried to send a private message to themselves.")
            else:
                clients[recipient].sendall(f"{sender}: {message}".encode())
                clients[sender].sendall(f"Delivered to {recipient}".encode())
                logging.info(f"{sender} -> {recipient} (private): {message}")
        except Exception as e:
            clients[sender].sendall(f"Delivery error to {recipient}: {e}".encode())
            logging.error(f"Error sending to {recipient}: {e}")
    else:
        clients[sender].sendall(f"User {recipient} not found".encode())
        logging.warning(f"{sender} tried to send to non-existent user {recipient}")

# Функция для обработки клиента
def handle_client(conn, addr):
    """
    Handle a single client connection: registration, message receiving and processing.

    Args:
        conn (socket.socket): Client socket.
        addr (tuple): Client address.
    """
    name = None
    try:
        # Запрос имени пользователя
        conn.sendall(b"Enter your name:")
        name = conn.recv(BUFFER_SIZE).decode().strip()
        # Проверка уникальности имени
        if not name or name in clients:
            conn.sendall(b"Name is taken or invalid. Disconnecting.")
            conn.close()
            return
        clients[name] = conn
        logging.info(f"{name} connected from {addr}")
        # Оповещение о новом пользователе
        broadcast(name, f"{name} has joined the chat!", False)
        conn.sendall(
            b"Welcome to the chat!\n"
            b"To send a private message: /w *nickname* *message*\n"
            b"To send a public message: just type your message."
        )
        # Основной цикл приема сообщений от клиента
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            msg = data.decode().strip()
            # Проверка на приватное сообщение
            if msg.startswith("/w "):
                try:
                    _, recipient_and_msg = msg.split("/w ", 1)
                    recipient, message = recipient_and_msg.strip().split(" ", 1)
                    send_private(name, recipient, message)
                except ValueError:
                    conn.sendall(b"Invalid private message format. Use: /w *nickname* *message*")
            else:
                broadcast(name, msg)
    # Обработка ошибок соединения
    except Exception as e:
        if isinstance(e, ConnectionResetError):
            pass
        else:
            logging.error(f"Client error {addr}: {e}")
    finally:
        # Отключение клиента и оповещение об этом
        if name and name in clients:
            broadcast(name, f"{name} has left the chat.", False)
            del clients[name]
            conn.close()
            logging.info(f"{name} disconnected")

# Запуск сервера
# Установка обработчика сигналов для корректного завершения
def main():
    """
    Start the chat server, accept connections and create threads for clients.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    server.settimeout(1.0)  # Прерывание для проверки наличия сигнала о остановке сервера
    logging.info(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            try:
                # Ожидание подключения клиента
                conn, addr = server.accept()
                # Для каждого клиента создается отдельный поток
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        logging.info("Server stopped by user.")
    finally:
        server.close()

if __name__ == "__main__":
    main()
