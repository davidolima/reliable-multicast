#!/usr/bin/env python3

import socket
import logging
import threading
from time import sleep

from utils import constants

logger = logging.getLogger(__name__)

class Client:
    def __init__(self) -> None:
        self._socket = None

        self._setup_socket()
        self._start_receive_loop()

    def __str__(self):
        assert self._socket is not None
        s = f'<Client {self._socket.getsockname()}>'
        return s

    def _start_receive_loop(self):
        def receive_loop():
            while self.is_connected():
                self.receive()

        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()

    def _setup_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('0.0.0.0', 0))
        self._socket.listen(1)

    def is_connected(self) -> bool:
        return (self._socket is not None)

    def disconnect(self) -> None:
        if not self.is_connected():
            logging.warn("Attempted to disconnect without a connection.")
            return
        assert (self._socket is not None) # NOTE: Just so LSP works properly

        self._socket.shutdown(0)
        self._socket.close()
        del self._socket
        self._socket = None

    def get_addr(self):
        assert self._socket is not None, "No open sockets in this client"
        return self._socket.getsockname()

    def crash(self, t: int = 0):
        sleep(t)
        id = str(self)
        self.disconnect()
        print(f"{id} crashed!")

    
    def _construct_message(self, dest_addr: str, m: str) -> bytes:

        msg = str({
            'sender': self.get_addr(),
            'dest': dest_addr,
            'content': m
        }).encode(constants.MSG_ENCODING)

        msg = b'<bof>' + msg + b'<eof>'
        print(msg)

        return msg

    def receive(self):
        if not self.is_connected():
            logger.info(f"[{self}] Could not start receiving messages in socket. Socket does not exist!")
            return

        assert self._socket is not None # Making Pyright shut up

        try:
            conn, addr = self._socket.accept()
            data = b''
            while True:
                block = conn.recv(1024)
                if not block:
                    break

                data += block
                if b'<eof>' in block:
                    break
            print(f"[{self}] Received message:", data.decode(constants.MSG_ENCODING))
            conn.close()

        except Exception as e:
            logger.error(f"{self} Error receiving message: {e}")

    def send(self, dest_addr: str, message: str):
        try:
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_sock.connect(dest_addr)

            encoded_msg = self._construct_message(dest_addr, message)
            print(f"[{self}] Sending message to {dest_addr}.")
            send_sock.send(encoded_msg)

        except Exception as e:
            logger.error(f"{self} Error sending message: {e}")
