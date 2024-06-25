import sys
import getopt
import socket
import random
from threading import Thread
import os
import util
import time

SIZE = 4096
FORMAT = "utf-8"


class Client:
    def __init__(self, username, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.name = username
        self.sock.connect((self.server_addr, self.server_port))
        self.close = False

    def start(self):
        join_message = f"join {self.name}"
        self.sock.send(join_message.encode(FORMAT))

        while True:

            if self.close:
                break

            user_input = input()
            input_list = user_input.split()
            try:
                command = input_list[0]

                if command == "list":
                    message = f"request_users_list {self.name}"
                    self.sock.send(message.encode(FORMAT))

                elif command == "msg":
                    recipient_count = int(input_list[1])
                    recipients = " ".join(input_list[2 : 2 + recipient_count])
                    send_message = "send_message"
                    temp_msg = " ".join(input_list[2 + recipient_count :])
                    message = (
                        f"{send_message} {recipient_count} {recipients} {temp_msg}"
                    )
                    self.sock.send(message.encode(FORMAT))

                elif command == "file":
                    file_name = input_list[-1]

                    with open(file_name, "r") as file:
                        file_content = file.read()
                    file.close()

                    file_message = f"{user_input} {file_content}"

                    self.sock.send(file_message.encode(FORMAT))

                elif command == "help":
                    pass
                elif command == "quit":
                    temp_msg = f"disconnect {self.name}"
                    self.sock.send(temp_msg.encode(FORMAT))
                    print("quitting")
                    break
                else:
                    print("Incorrect userinput format")
            except Exception as e:
                pass

    def receive_handler(self):
        while True:
            try:
                message = self.sock.recv(4096).decode("utf-8").strip()
                if message:
                    msg_list = message.split()

                    if msg_list[0] == "forward_message":

                        sender_username = msg_list[1]
                        message_content = " ".join(msg_list[2:])

                        print(f"msg: {sender_username}: {message_content}")

                    elif msg_list[0] == "response_users_list":
                        message_content = " ".join(msg_list[1:])
                        print(f"list: {message_content}")

                    elif msg_list[0] == "forward_file":
                        sender_un = msg_list[1]
                        file_name = msg_list[2]
                        content = " ".join(msg_list[3:])
                        updated_filename = f"{self.name}_{file_name}"

                        with open(updated_filename, "w") as file:
                            file.write(content)
                        file.close()

                        print(f"file: {sender_un}: {file_name}")

                    elif msg_list[0] == "err_server_full":
                        print("disconnected: server full")
                        self.sock.close()
                        self.close = True
                        break

                    elif msg_list[0] == "err_unknown_message":
                        print("disconnected: server received unknown command")
                        self.sock.close()
                        self.close = True
                        break

                    elif msg_list[0] == "err_username_unavailable":
                        print("disconnected: username not available")
                        self.sock.close()
                        self.close = True
                        break

                    elif msg_list[0] == "disconnect":
                        username = msg_list[1]
                        print(f"disconnected: {username}")
                        self.sock.close()
                        self.close = True
                        break

            except Exception as e:
                pass


if __name__ == "__main__":

    def helper():
        """
        This function is just for the sake of our Client module completion
        """
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print(
            "-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost"
        )
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(
            sys.argv[1:], "u:p:a", ["user=", "port=", "address="]
        )
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
