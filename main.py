#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])

from app.client import Client

if __name__ == '__main__':
    group = [Client(), Client()]

    for p in group:
        print(p)

    m = 'Hello world!'
    group[0].send(group[1].get_addr(), m)
    #P[0].multicast(P[1:], m)
