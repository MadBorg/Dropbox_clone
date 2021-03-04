import socket
import os
import pickle
import time
from shutil import rmtree
import test_homework
from pathlib import Path

MAX_PACKET_SIZE = 1024


class Server:
    s: socket.socket
    port: int
    header_length: int

    def __init__(self, port: int, header_length: int) -> None:
        print(
            f"Starting Server on: PID: {os.getpid()}, PORT: {port}")
        self.port = port
        self.header_length = header_length

        # Server socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # To solve not able to reuse socket
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Make server
        self.s.bind((socket.gethostname(), port))
        # Listen que size
        self.s.listen(5)

    def start(self):
        # Start accepting
        clientsocket, address = self.s.accept()
        print(f"Connection from {address} has bean established!")
        while True:
            # if any connect accept, client socket obj, address: ip/id
            print("Waiting for msg")
            msg = self._receive_msg(client_socket=clientsocket)
            self.s.close()
            yield msg

    def _receive_msg(self, client_socket):
        """Receiving messages from the client socket"""
        # Recv header to know the size of the data
        message_header = client_socket.recv(self.header_length)
        # If no size or size = 0, return default value
        if not (len(message_header)):
            return {"header": f"{0:<{10}}", "data": None}
        # Decode message size to int
        message_length = int(message_header.decode("utf-8").strip())

        data = []
        current_size = 0
        # receive data until current size of data is the size of message length
        while current_size < message_length:
            packet = client_socket.recv(
                # Using min here to make sure we are only using the needed buffersize
                min(message_length-current_size, MAX_PACKET_SIZE))
            current_size += len(packet)
            data.append(packet)
        # Return data and decode with pickle.
        return {
            "header": message_header,
            "data": pickle.loads(b"".join(data))
        }


class DropboxServer:
    # Path to DropboxServer directory
    path: str
    # Server object to receive messages
    server: Server

    def __init__(self, port: int, header_length: int, path: str) -> None:
        self.server = Server(port=port, header_length=header_length)
        self.path = path

    def start(self):
        """Starting the DropboxServer"""
        # Update is a generator obj, where next is the next data pkg.
        update = self.server.start()
        # Infinite loop, running each time the server recives a pkg.
        for updates in update:
            print("Server: Waiting for updates")
            # If loss of contact start new server and sleep
            if updates["data"] == None:
                print("Connection lost trying to accept new connection")
                update = self.server.start()
                time.sleep(1.0)
                continue
            # Else sync server with updates
            print("Server: syncing...")
            # Updating dir
            self.update_path(updates["data"])
            # Printing files updated
            print("Updates:\n{}".format(
                "   " + "\n   ".join(u[0] for u in updates["data"])))

    def update_path(self, updates):
        """Looping over the updates and implements them"""
        path = self.path
        for update in updates:
            # is size -1 remove file or dir
            if update[2] == -1:
                if update[1] == "dir":
                    rmtree(f"{path}/{update[0]}")
                else:
                    os.remove(f"{path}/{update[0]}")
            # Else update or add
            else:
                if update[1] == "file":
                    test_homework.spit(f"{path}/{update[0]}", update[3])
                else:  # == dir
                    Path(
                        f"{path}/{update[0]}").mkdir(parents=True, exist_ok=True)
