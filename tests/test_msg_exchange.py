#!/usr/bin/env python3

from app.client import Client

def test_send_message():
    """
    Test: Sending a big message.
    """

    c1 = Client()
    c2 = Client()

    m = 'Hello world!'*2048
    c1.send(c2.get_addr(), m)
