#!/usr/bin/env python3

import os
import socket
import logging
import threading
import uuid
from time import sleep
from typing import *
from app.lamport_clock import LamportClock

from ast import literal_eval

from utils import constants

logger = logging.getLogger(__name__)

class Client:
    def __init__(self) -> None:
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self.clock = LamportClock()

        self._setup_socket()
        self._start_receive_loop()
        self.received_messages: list[str] = []
        # Track delivered messages (origin, content) to prevent duplicates
        self._delivered: set[tuple[tuple[str, int], str]] = set()

    def __str__(self):
        assert self._socket is not None
        return f'<Client {self._socket.getsockname()}>'

    def _start_receive_loop(self):
        def receive_loop():
            while self.is_connected():
                try:
                    m = self._sock_receive()
                    if m:
                        self.r_deliver(m)
                except Exception as e:
                    if not self.is_connected():
                        break
                    logger.warning(f"Receive error (client may have crashed): {e}")

        self._thread = threading.Thread(target=receive_loop, daemon=True)
        self._thread.start()

    def _setup_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('127.0.0.1', 0))
        self._socket.listen(1)

    def is_connected(self) -> bool:
        return self._socket is not None

    def disconnect(self) -> None:
        if not self.is_connected():
            logging.warning("Attempted to disconnect without a connection.")
            return
        assert self._socket is not None

        try:
            self._socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._socket.close()
        self._socket = None

    def get_addr(self) -> Tuple[str, int]:
        assert self._socket is not None, "No open sockets in this client"
        return self._socket.getsockname()

    def crash(self, t: int = 0, simulate=False):
        sleep(t)
        id_str = str(self)
        self.disconnect()
        print(f"{id_str} crashed!")
        if not simulate:
            os._exit(0)

    def _construct_message(self, dest_addr: tuple[str, int], m: str, message_id: str, **kargs) -> bytes:
        msg_dict = {
            'message_id': message_id,
            'sender': self.get_addr(),
            'dest': dest_addr,
            'content': m,
            'clock': self.clock.time,
            **kargs
        }
        msg = str(msg_dict).encode(constants.MSG_ENCODING)
        return b'<bof>' + msg + b'<eof>'

    def _sock_receive(self) -> str:
        if not self.is_connected():
            logger.fatal(f"[{self}] Socket missing for receive loop.")
            quit(1)

        assert self._socket is not None
        try:
            conn, _ = self._socket.accept()
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
        message_id = str(uuid.uuid4())
        pkg = self._construct_message(dest_addr, message, message_id=message_id)
        self.send_raw(dest_addr, pkg)

    def send_raw(self, dest_addr: tuple[str, int], pkg: bytes):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as send_sock:
                send_sock.connect(dest_addr)
                logger.info(f"{self} Sending message to {dest_addr}. | Timestamp de Envio: {self.clock.time}")
                send_sock.send(pkg)
        except Exception as e:
            logger.error(f"{self} Error sending message: {e}")

    def r_multicast(self, message: str, group: list[tuple], crash_after: Optional[int] = None, simulate: bool = False, originated_locally: bool = False, message_id: Optional[str] = None):
        if not message_id:
            message_id = str(uuid.uuid4())

        if not originated_locally:
            pkg_self = self._construct_message(dest_addr=self.get_addr(), m=message, group=group, message_id=message_id)
            self.r_deliver(pkg_self.decode(constants.MSG_ENCODING))
            return

        send_count = 0
        
        for addr in group:
            pkg = self._construct_message(dest_addr=addr, m=message, group=group, message_id=message_id)
            if crash_after is not None and send_count == crash_after:
                self.crash(simulate=simulate)
                return
            self.send_raw(addr, pkg)
            self.clock.increment()
            send_count += 1

    def r_deliver(self, raw_m: str):
        try:
            inner = raw_m.split('>')[1].rsplit('<', 1)[0]
            obj_m = literal_eval(inner)
            if not isinstance(obj_m, dict):
                raise ValueError("Mensagem não é um dicionário")
        except Exception:
            logger.error(f"{self} Invalid message format: {raw_m}")
            return

        sender = tuple(obj_m.get('sender', []))
        content = obj_m.get('content')
        if content is None:
            logger.warning(f"{self} Mensagem sem conteúdo: {raw_m}")
            return

        message_id = obj_m.get('message_id')
        if message_id is None or message_id in self._delivered:
            return
        
        received_time = obj_m.get('clock', 0)
        self.clock.update(received_time)

        self._delivered.add(message_id)
        self.received_messages.append(content)
        logger.info(f"{self} Received message: {content} | Timestamp de Entrega: {self.clock.time}")

        group: list[tuple] = obj_m.get('group', [])
        try:
            group.remove(self.get_addr())
        except ValueError:
            pass
        self.r_multicast(content, group, originated_locally=True, message_id=message_id)
