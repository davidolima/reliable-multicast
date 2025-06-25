#!/usr/bin/env python3

import json
import socket
import logging
import threading
from time import sleep
from typing import *

from ast import literal_eval

from utils import constants

logger = logging.getLogger(__name__)

class Client:
    def __init__(self) -> None:
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None

        self._setup_socket()
        self._start_receive_loop()

    def __str__(self):
        assert self._socket is not None
        s = f'<Client {self._socket.getsockname()}>'
        return s

    def _start_receive_loop(self):
        def receive_loop():
            while self.is_connected():
                try:
                    m = self._sock_receive()
                    self.r_deliver(m)
                except Exception as e:
                    logger.warn(f"{self}: {e}")

        self._thread = threading.Thread(target=receive_loop, daemon=True)
        self._thread.start()

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

    def get_addr(self) -> Tuple[str, int]:
        assert self._socket is not None, "No open sockets in this client"
        return self._socket.getsockname()

    def crash(self, t: int = 0):
        sleep(t)
        id = str(self)
        self.disconnect()
        print(f"{id} crashed!")
        quit(0)
    
    def _construct_message(self, dest_addr: tuple[str, int], m: str, **kargs) -> bytes:
        msg = str({
            'sender': self.get_addr(),
            'dest': dest_addr,
            'content': m,
            **kargs
        }).encode(constants.MSG_ENCODING)

        msg = b'<bof>' + msg + b'<eof>'
        return msg

    def _sock_receive(self) -> str:
        if not self.is_connected():
            logger.fatal(f"[{self}] Could not start receiving messages in socket. Socket does not exist!")
            quit(0)

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

            conn.close()

            return data.decode(constants.MSG_ENCODING)

        except Exception as e:
            logger.error(f"{self} Error receiving message: {e}")

        return ''

    def send(self, dest_addr: tuple[str, int], message: str):
        pkg = self._construct_message(dest_addr, message)
        self.send_raw(dest_addr, pkg)

    def send_raw(self, dest_addr: tuple[str, int], pkg: bytes):
        """
        Para ser usado para o envio de dados brutos, em bytes.
        Para o nosso propósito, a não ser que saiba o que está fazendo,
        Utilize após utilização do método _construct_message()
        """
        try:
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_sock.connect(dest_addr)

            logger.info(f"{self} Sending message to {dest_addr}.")
            send_sock.send(pkg)

        except Exception as e:
            logger.error(f"{self} Error sending message: {e}")


    def r_multicast(self, message: str, group: list[tuple], crash_after: Optional[int] = None):
        for i, addr in enumerate(group):
            if (crash_after is not None and i == crash_after):
                self.crash()
                return

            pkg = self._construct_message(m=message, dest_addr=addr, group=group)
            self.send_raw(addr, pkg)

    def r_deliver(self, raw_m: str):
        try:
            m = raw_m[raw_m.index('>')+1:raw_m.rindex('<')] # remover delimitadores (<bof> e <eof>)

        except ValueError:
            logger.error(f"{self} Message received, but in invalid format: {raw_m}")
            return

        obj_m = literal_eval(m) # extrai dict da str recebida
        logger.info(f"{self} Received message: {obj_m['content']}")

        group: list[tuple] = obj_m['group']
        group.remove(self.get_addr()) # Remove si mesmo do grupo dos processos que devem receber a mensagem

        self.r_multicast(obj_m['content'], group)
