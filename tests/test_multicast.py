import time
import logging
from app.client import Client

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def wait_delivery():
    time.sleep(1.5)  


def test_basic_send():
    print("\n=== Teste: Envio básico de mensagem ===")
    c1 = Client()
    c2 = Client()

    logging.info(f"Cliente 1: {c1.get_addr()} envia para Cliente 2: {c2.get_addr()}")
    print(f"[INFO] Cliente 1: {c1.get_addr()} envia para Cliente 2: {c2.get_addr()}")
    c1.send(c2.get_addr(), "basic message")
    wait_delivery()

    assert "basic message" in c2.received_messages, "Cliente 2 não recebeu a mensagem corretamente"
    logging.info("[OK] Cliente 2 recebeu a mensagem com sucesso.")
    print("[OK] Cliente 2 recebeu a mensagem com sucesso.")
    print("=== Fim do teste ===\n")


def test_multicast_to_group():
    print("\n=== Teste: Envio multicast para grupo ===")
    group = [Client() for _ in range(3)]
    addrs = [c.get_addr() for c in group]

    logging.info("Cliente 0 enviando mensagem para o grupo")
    print("[INFO] Cliente 0 enviando mensagem para o grupo")
    group[0].r_multicast("group hello", addrs)
    wait_delivery()

    for i, client in enumerate(group[1:], start=1):
        assert "group hello" in client.received_messages, f"Cliente {i} não recebeu a mensagem multicast"
        logging.info(f"[OK] Cliente {i} recebeu a mensagem multicast.")
        print(f"[OK] Cliente {i} recebeu a mensagem multicast.")
    print("=== Fim do teste ===\n")


def test_multicast_with_crash_simulated():
    print("\n=== Teste: Multicast com crash simulado ===")
    group = [Client() for _ in range(4)]
    addrs = [c.get_addr() for c in group]

    logging.info("Cliente 0 iniciando envio com crash após 2 envios")
    print("[INFO] Cliente 0 iniciando envio com crash após 2 envios")
    group[0].r_multicast("crash test", addrs, crash_after=2, simulate=True)
    wait_delivery()

    for i, client in enumerate(group[1:], start=1):
        count = client.received_messages.count("crash test")
        assert count == 1, f"Cliente {i} recebeu a mensagem múltiplas vezes: {count}"
        logging.info(f"[OK] Cliente {i} recebeu a mensagem exatamente uma vez.")
        print(f"[OK] Cliente {i} recebeu a mensagem exatamente uma vez.")
    
    print("=== Fim do teste ===\n")
    

def test_malformed_message():
    print("\n=== Teste: Mensagem malformada ===")
    c1 = Client()
    c2 = Client()

    logging.info("Cliente 1 enviando mensagem malformada para Cliente 2")
    print("[INFO] Cliente 1 enviando mensagem malformada para Cliente 2")
    c1.send_raw(c2.get_addr(), b"<bof>{'invalid':'message'}<eof>")
    wait_delivery()

    # Como a mensagem é malformada, o cliente não deve registrá-la
    assert len(c2.received_messages) == 0, "Cliente 2 registrou mensagem malformada incorretamente"
    logging.info("[OK] Cliente 2 ignorou a mensagem malformada como esperado.")
    print("[OK] Cliente 2 ignorou a mensagem malformada como esperado.")
    print("=== Fim do teste ===\n")
