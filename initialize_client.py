from app.client import Client
from ast import literal_eval
from typing import *

import logging
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])


def initialize_cli(client: Client):
    print("You are", client)

    running = True
    while running:
        cmd = input(">> ")
        running = interpret_cmd(client, cmd)


def interpret_cmd(client: Client, raw_cmd: str) -> bool:
    cmd: list[str] = raw_cmd.split(' ')
    match cmd[0]:
        case 'quit':
            return False
        case 'send':
            if len(cmd) < 3:
                return show_help()

            try:
                msg = cmd[1]
                group = literal_eval(cmd[2])
            except Exception as e:
                print(f"[ERROR] Error reading arguments: {e}")
                return show_help()

            
            client.r_multicast(msg, group, originated_locally=True)

        case 'sendcrash':
            if len(cmd) < 4:
                return show_help()

            try:
                msg = cmd[1]
                crash_after = int(cmd[2])
                group = literal_eval(cmd[3])
            except Exception as e:
                print(f"[ERROR] Error reading arguments: {e}")
                return show_help()

            client.r_multicast(msg, group, crash_after=crash_after, originated_locally=True)

        case 'help':
            return show_help()

        case '':
            return True

        case _:
            return show_help()


    return True

def show_help() -> Literal[True]:
    print("Available commands:")
    print('  help - Shows this help message')
    print('  quit - Exits program')
    print('  send <message> [(ip1, addr1),(ip2, addr2),...] - Multicasts <message> to specified group of processes.')
    print('  sendcrash <message> <successes> [(ip1, addr1),(ip2, addr2),...] - Multicasts <message> to specified group of processes, but crashes after sending to <successes> processes.')
    print('')

    return True

if __name__ == '__main__':
    client = Client()

    initialize_cli(client)
    #send Hello-world! [('0.0.0.0',35821),('0.0.0.0',57965)]
    #sendcrash Hello-world! 1 [('0.0.0.0',35837),('0.0.0.0',47603)]
