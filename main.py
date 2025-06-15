#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

from app.client import Client

if __name__ == '__main__':
    P = [Client(), Client()]

    for p in P:
        print(p)

    m = 'Hello world!'

    P[0].send(P[1].get_addr(), m)
    #P[0].multicast(P[1:], m)
