import socket


class Bot():
    def __init__(self):
        self.host = 'localhost'
        self.port = 40037

    def send_message(self, message):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            s.send(message)
            s.close()
        except Exception:
            pass

bot = Bot()
