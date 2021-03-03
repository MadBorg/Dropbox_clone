import socket
import os
import pickle
import time
from shutil import rmtree
from test_homework import server, spit


class Server:
    s: socket.socket
    port: int
    header_length: int

    def __init__(self, port: int, header_length: int) -> None:
        print(f"Starting Server on: PID: {os.getpid()}")
        self.port = port
        self.header_length = header_length

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((socket.gethostname(), port))
        self.s.listen(5)

    def start(self):
        # que of 5
        clientsocket, address = self.s.accept()

        while True:
            # if any connect accept, client socket obj, address: ip/id
            print("Waiting for msg")
            print(f"Connection from {address} has bean established!")
            msg = self._receive_msg(client_socket=clientsocket)
            print(f"Got msg:")
            print(msg)
            yield msg

    def _receive_msg(self, client_socket):
        try:
            message_header = client_socket.recv(self.header_length)
            if not (len(message_header)):
                return {"header": f"{0:<{10}}", "data": None}
            message_length = int(message_header.decode("utf-8").strip())

            return {
                "header": message_header,
                "data": pickle.loads(client_socket.recv(message_length))
            }
        except Exception as e:
            print(f"{e}")
            return {"header": f"{0:<{10}}", "data": None}


class DropboxServer(server):
    path: str

    def __init__(self, port: int, header_length: int, path: str) -> None:
        super().__init__(port=port, header_length=header_length)
        self.path = path

    def start(self):
        for updates in super().start():
            if updates["data"] == None:
                print("No update, sleeping 1 second.")
                time.sleep(1.0)
                continue

            print("Server syncing...")
            self.update_path(updates)
            print(f"Updates:\n{'\n'.join(updates)}")
            print("Server sleeping 1 second.")
            time.sleep(1.0)

    def update_path(self, updates):
        path = self.path
        for update in updates:
            # is size -1 rm
            if update[2] == -1:
                if update[1] == "dir":
                    rmtree(f"{path}/{update[0]}")
                else:
                    os.remove(f"{path}/{update[0]}")
            else:
                if update[1] == "file":
                    spit(f"{path}/{update[0]}", update[3])
                else:  # == dir
                    os.makedirs(f"{path}/{update[0]}")


if __name__ == "__main__":
    s = Server(
        1234,
        10
    )
    s.start()
