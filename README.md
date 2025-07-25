# Realiable Multicast com Relógio Lógico de Lamport

## Resumo
Reste repositório contém o projeto prático produzido para a disciplina MATA88 - Fundamentos de Sistemas Distribuídos na Universidade Federal da Bahia (UFBA), ministrada pelo professor Raimundo José de Araújo Macêdo. O trabalho consiste em desenvolver uma aplicação distribuída em ambiente assíncrono que implemente o protocolo _Reliable Multicast_ entre processos e associe a cada mensagem entregue o valor do Relógio de _Lamport_.

## Grupo
 - David Lima
 - Mateus Seabra
 - Breno Cupertino
 - Otávio Novais
 - Júlia Mattos
 
## Execução do código

``` sh
$ python3 ./main.py
```

Alternativamente, abra diferentes terminais, e em cada um execute o comando

``` sh
$ python3 ./initialize_client.py
```

Para entrar numa interface de linha de comando (CLI) interativa para interagir com os outros processos. Os comandos disponíveis no CLI são:

### Comandos disponíveis no CLI
 - `quit`: Sai do CLI e interrompe a execução do código.
 
 - `send`: A partir do protocolo multicast implementado, envia uma mensagem para os processos especificados.
   - Uso: 
     - `>> send <message> [('ip1',port1),('ip2',port2),...]`
   - Ex.: Enviar mensagem "hello-world!" para os processos de IP 127.0.0.1:12345 e 127.0.0.1:54321
     - `>> send hello-world! [('127.0.0.1',12345),('127.0.0.1',54321)]`
   
 - `sendcrash`: A partir do protocolo multicast implementado, envia uma mensagem para os processos especificados.
   - Uso: 
     - `>> sendcrash <message> <successes> [('ip1',port1),('ip2',port2),...]`
   - Ex.: Enviar mensagem "hello-world!" para os processos de IP 127.0.0.1:12345 e 127.0.0.1:54321 e falhar (crash) após o primeiro envio
     - `>> sendcrash hello-world! 1 [('127.0.0.1',12345),('127.0.0.1',54321)]`

- `test_multicast`: Valida o código com casos de teste automáticos para cumprir as funções do reliable multicast.
   - Uso: 
     - `>> pytest -v -s tests/test_multicast.py`
