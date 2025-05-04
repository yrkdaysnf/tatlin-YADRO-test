"""Chat client"""

import socket
import threading

# Константы, совпадают с сервером
HOST = 'localhost'
PORT = 54321

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Подключение к серверу
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print(f"Connection to {HOST}:{PORT} refused. Is the server running?")
    exit(0)

def receive():
    """
    Receive messages from the server and print them to the console.
    """
    while True:
        # Получение и вывод сообщений от сервера
        try:
            message = client.recv(1024).decode('ascii')
            print(message)
        # Если соединение разорвано сервером
        except:
            print("Server terminated the connection. Press Enter to exit.")
            break

def write():
    """
    Read user input from the console and send it to the server.
    """
    # Чтение пользовательского ввода и отправка на сервер
    try:
        while True:
            message = input()
            client.send(message.encode('ascii'))
    # Обработка выхода пользователя по Ctrl+C
    except KeyboardInterrupt:
        print("\nExiting chat...")
        client.close()
        exit(0)

if __name__ == "__main__":
    # Запуск потока для приема сообщений от сервера
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()
    
    # Основной поток — отправка сообщений на сервер
    write()
