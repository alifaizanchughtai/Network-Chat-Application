import sys
import getopt
import socket
import util
import threading

FORMAT = "utf_8"
USERNAME = ""


class Server:
    def __init__(self, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.connected_clients = []
        self.close = False

    def start(self):
        self.sock.listen(util.MAX_NUM_CLIENTS + 1)
        while True:
            if self.close:
                break

            try:
                conn, _ = self.sock.accept()
                threading.Thread(target=self.client_handler, args=(conn,)).start()
            except Exception as e:
                pass

    def client_handler(self, conn):
        try:
            while True:
                msg = conn.recv(4096).decode("utf-8")
                msg_list = msg.split()
                command = msg_list[0]
                if not msg:
                    break

                if command == "join":
                    username = msg_list[1]
                    USERNAME = msg_list[1]
                    if len(self.connected_clients) >= util.MAX_NUM_CLIENTS:
                        error_message = "err_server_full"
                        conn.send(error_message.encode("utf-8"))
                        print("disconnected: server full")

                    elif any(
                        client[0] == username for client in self.connected_clients
                    ):
                        error_message = "err_username_unavailable"

                        conn.send(error_message.encode("utf-8"))
                        print("disconnected: username not available")
                    else:
                        new_client = (username, conn)
                        self.connected_clients.append(new_client)
                        print(f"join: {username}")

                elif command == "help":
                    help_message = """Supported commands:
                            - msg <recipient_count> <recipient_1> <recipient_2> ... <recipient_n> <message>: Send a message to one or more recipients.
                            - list: List all connected users.
                            - file <recipient_count> <recipient_1> ... <recipient_n> <file_name>: Send a file to one or more recipients.
                            - help: Display this help message."""
                    conn.send(help_message.encode(FORMAT))
                elif command == "disconnect":
                    disconnected_client = None
                    for client in self.connected_clients:
                        if client[1] == conn:
                            disconnected_client = client
                            self.connected_clients.remove(disconnected_client)
                            conn.close()
                            print(f"disconnected: {disconnected_client[0]}")
                            self.close = True
                            break

                elif command == "request_users_list":
                    connected_users = " ".join(
                        sorted([client[0] for client in self.connected_clients])
                    )
                    list_message = f"response_users_list {connected_users}"
                    username = msg_list[1]
                    conn.send(list_message.encode("utf-8"))
                    print(f"request_users_list: {username}")

                elif command == "send_message":

                    recipient_count = int(msg_list[1])
                    recipients = msg_list[2 : 2 + recipient_count]

                    counter_flag = False

                    recipient_list = set()

                    temp_msg = " ".join(msg_list[2 + recipient_count :])
                    for recipient in recipients:
                        if recipient not in recipient_list:
                            if recipient in [
                                client[0] for client in self.connected_clients
                            ]:
                                for tuple in self.connected_clients:
                                    if tuple[0] == recipient:
                                        msg_x = f"forward_message {USERNAME} {temp_msg}"
                                        recipient_socket = tuple[1]
                                        recipient_socket.send(msg_x.encode("utf-8"))
                                        msg_x = ""
                                        recipient_list.add(recipient)
                                counter_flag = True
                            else:
                                print(
                                    f"msg: {USERNAME} to non-existent user {recipient}"
                                )

                    if counter_flag:
                        print(f"msg: {USERNAME}")

                elif command == "file":
                    print(f"file: {USERNAME}")
                    recipient_count = int(msg_list[1])
                    file_name = msg_list[2 + recipient_count]
                    file_content = " ".join(msg_list[2 + recipient_count + 1 :])
                    recipients = msg_list[2 : 2 + recipient_count]
                    recipient_list = set()

                    for recipient in recipients:
                        if recipient not in recipient_list:
                            if recipient in [
                                client[0] for client in self.connected_clients
                            ]:
                                for tuple in self.connected_clients:
                                    if tuple[0] == recipient:
                                        msg_x = f"forward_file {USERNAME} {file_name} {file_content}"
                                        recipient_socket = tuple[1]
                                        recipient_socket.send(msg_x.encode("utf-8"))
                                        msg_x = ""
                                        recipient_list.add(recipient)
                                counter_flag = True
                            else:
                                print(
                                    f"file: {USERNAME} to non-existent user {recipient}"
                                )

        except Exception as e:
            # print(f"An error occurred with a client: {e}")
            pass


if __name__ == "__main__":

    def helper():
        """
        This function is just for the sake of our module completion
        """
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print(
            "-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost"
        )
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:], "p:a", ["port=", "address="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
