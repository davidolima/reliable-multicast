#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

from app import client
from app.client import Client

if __name__ == '__main__':
    client_group = [Client(), Client(), Client()]
    addrs = [c.get_addr() for c in client_group]

    for p in client_group:
        print(p)

    m = 'Hello world!'
    client_group[0].r_multicast(m, addrs,  crash_after=2)
    #P[0].multicast(P[1:], m)
