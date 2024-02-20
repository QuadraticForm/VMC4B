import threading
from typing import Union
from threading import Thread
from collections import deque
from datetime import datetime
from ..core.pythonosc.dispatcher import Dispatcher
from ..core.pythonosc.osc_server import BlockingOSCUDPServer


class OscThreadServer():

    def __init__(self):
        self.thread: Union[Thread, None] = None
        self.server: Union[BlockingOSCUDPServer, None] = None
        self.queue: deque = deque([])

    def is_alive(self):
        return (self.thread is not None) or (self.server is not None)

    def osc_server_thread(self, ip: str, port: int):
        dispatcher = Dispatcher()

        def queueing(address, *args):
            self.queue.append({"timestamp": datetime.now(),
                              "address": address, "args": args})

        dispatcher.set_default_handler(queueing)

        self.server = BlockingOSCUDPServer((ip, port), dispatcher)
        self.server.serve_forever()
        self.server = None

    def start(self, ip, port):
        if self.server is not None:
            raise Exception("Another server is already exist")
        if self.thread is not None:
            raise Exception("Another thread is still alive")
        self.thread = threading.Thread(
            target=self.osc_server_thread, args=(ip, port))
        self.thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
        self.thread.join()
        self.thread = None
        self.queue.clear()
