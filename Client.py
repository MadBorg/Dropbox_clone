import os
import pickle
import socket
import test_homework
import time


class Client:
    s: socket.socket
    header_size: int
    port: int

    def __init__(self, port: int, header_size: int) -> None:
        self.header_size = header_size
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host_name=socket.gethostname()):
        print(f"Starting client on: PID: {os.getpid()}")
        self.s.connect((host_name, self.port))

    def send(self, msg: bytes):
        # Sending header with size information
        print("Sending message")
        print(msg)
        msg = pickle.dumps(msg)
        self.s.send(bytes(f"{len(msg):<{self.header_size}}", "utf-8"))
        # Sending message
        self.s.send(msg)


class DropboxClient:
    path: str
    state_hash: str
    client: Client
    state_string: set

    def __init__(self, port: int, header_length: int, path: str) -> None:
        self.client = Client(port=port, header_length=header_length)
        self.path = path
        self.state_string = self.get_new_state_string()

    def start(self, host_name=socket.gethostname()):

        self.client.start(host_name)
        # 1st send is all content
        print("Sending original state")
        self.client.send(
            self.get_updates(self.state_string, "")
        )
        # If state changes send update
        while True:
            new_state_string = self.get_new_state_string()
            if self.state_string != new_state_string:
                # Update
                print("Client sending updates.")
                self.client.send(self.get_updates(
                    self.state_string, new_state_string))
            print("Client sleeping 1 second.")
            time.sleep(1)

    def get_new_state_string(self):
        return test_homework.path_content_to_hash(self.path)

    def get_updates(self, new_state_string, old_state_string):
        path = self.path
        new_set = set(new_state_string.split("\n"))
        old_set = set(old_state_string.split("\n"))
        updates = new_set - old_set
        r = [(
            update[0],
            update[1],
            update[2],
            open(f"{path}/{update[0]}", "r").read()
        ) for update in updates]

        # removed files
        old_paths = {val[0]: val for val in old_set}
        new_paths = {val[0]: val for val in new_set}

        return sorted(r + [(path, old_paths[path][1], -1, "") for path in old_paths if path not in new_paths])


if __name__ == "__main__":
    c = Client(
        header_size=test_homework.HEADER_SIZE,
        port=test_homework.PORT,
    )
    c.start()

    import IPython
    IPython.embed()
