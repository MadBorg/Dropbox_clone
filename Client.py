import os
import pickle
import socket
from typing import List, Tuple
import test_homework
import time


class Client:
    # The TCP socket
    s: socket.socket
    # The size of the the header package.
    header_size: int
    # Service port
    port: int

    def __init__(self, port: int, header_size: int) -> None:
        """Setting up the client"""
        self.header_size = header_size
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host_name=socket.gethostname()) -> None:
        """Starting client, and connecting to host."""
        print(f"Starting client: PID: {os.getpid()}, port: {self.port}")
        self.s.connect((host_name, self.port))

    def send(self, msg) -> None:
        # Sending header with size information
        print("Sending message")
        # Using pickling to decode python object
        msg: bytes = pickle.dumps(msg)
        # Sending header with size information
        self.s.send(bytes(f"{len(msg):<{self.header_size}}", "utf-8"))
        # Sending data.
        self.s.send(msg)

    def __exit__(self, exc_type, exc_value, traceback):
        self.s.close()


class DropboxClient:
    # Path to Client directory
    path: str
    # Client for sending data
    client: Client
    # Value of the state, to check for updates
    state: List[Tuple]

    def __init__(self, port: int, header_length: int, path: str) -> None:
        self.client = Client(port=port, header_size=header_length)
        self.path = path
        # Getting initial state
        self.state = self.get_new_state()

    def start(self, host_name=socket.gethostname()):
        """Starting the DropboxClient with a infinite loop"""
        # Starting client
        self.client.start(host_name)
        # send all content
        print("Sending original state")
        self.client.send(
            self.get_updates(new_state=self.state, old_state="")
        )
        # No breakpoint, so infinite
        while True:
            # If state changes send update
            new_state = self.get_new_state()
            if self.state != new_state:
                # Update
                print("Client sending updates.")
                self.client.send(self.get_updates(
                    old_state=self.state, new_state=new_state))
                self.state = new_state
            else:  # If no update sleep one second
                time.sleep(1)
            print("Client sleeping 1 second.")

    def get_new_state_string(self):
        return test_homework.path_content_to_hash(self.path)

    def get_new_state(self) -> List[Tuple]:
        return test_homework.path_to_hashed_tuples(self.path)

    def get_updates(self, new_state: List[Tuple], old_state: List[Tuple]):
        """
        Using the new and old state to gather the updates.

        Returning a List of tuples similar to the state variables, but instead of a hash it contains the actual data
        """
        path = self.path
        # Find the updates in the new state
        new_set = set(new_state)
        old_set = set(old_state)
        updates = new_set - old_set

        # Read the updates if file else just add the state value
        r = [(
            update[0],
            update[1],
            update[2],
            open(f"{path}/{update[0]}", "r").read()
        ) if update[1] == "file" else (
            update
        ) for update in updates]

        # Adding the removed files and folders with size of -1 to show they need to be removed
        old_paths = {val[0]: val for val in old_set}
        new_paths = {val[0]: val for val in new_set}
        rm = [(path, old_paths[path][1], -1, "")
              for path in old_paths if path not in new_paths]
        return sorted(r + rm)
