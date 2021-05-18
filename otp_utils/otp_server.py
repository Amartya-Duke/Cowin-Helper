import datetime
import re
import socket
import threading
import time

from CowinHelper.config import OTP_UTILS

TIMESTAMP_SEPARATOR = "___"
OTP_REGEX = r'[0-9]+'

OTP_MESSAGE_REGEX = r'Your OTP to register\\\\/access CoWIN is [0-9]+[.]'

headers = """\
POST /auth HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

body = 'Ok'
body_bytes = body.encode('ascii')
header_bytes = headers.format(
    content_type="application/x-www-form-urlencoded",
    content_length=len(body_bytes),
    host=str(OTP_UTILS['SERVER_HOST']) + ":" + str(OTP_UTILS['SERVER_PORT'])
).encode('iso-8859-1')

response_payload = header_bytes + body_bytes


class OTP_SERVER:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def process_client(self, client_socket):
        start_time = time.time()
        content = b''
        with client_socket:
            while True:
                data = client_socket.recv(1024)
                content += data
                if not data or (re.search(OTP_MESSAGE_REGEX, str(content))):
                    client_socket.sendall(response_payload)
                    break

        otp_message = re.search(OTP_MESSAGE_REGEX, str(content)).group()
        print(otp_message)
        try:
            otp = re.search(OTP_REGEX, otp_message).group()
            with open(OTP_UTILS['OTP_STORE_PATH'], 'w') as f:
                timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
                content = "{timestamp}{timestamp_separator}{otp}".format(timestamp=timestamp,
                                                                         timestamp_separator=TIMESTAMP_SEPARATOR,
                                                                         otp=otp)
                f.write(content)
                print("Otp written to file {file}. {content}".format(file=f.name, content=content))
        except Exception as e:
            print(e)

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(10)
        self.socket = s
        print("Socket created. Server running at {}:{}".format(self.host, self.port))

        while True:
            conn, addr = self.socket.accept()
            print("New client connected: {}".format(addr))
            p = threading.Thread(target=self.process_client, args=(conn,))
            p.start()
            print("Listening for next connection")

    def stop(self):
        self.socket.close()
        print("Socket closed. Connection terminated")


server = OTP_SERVER(OTP_UTILS['SERVER_HOST'], OTP_UTILS['SERVER_PORT'])
server.start()
