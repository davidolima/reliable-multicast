# Realiable Multicast com Relógio Lógico de Lamport

## Resumo
Reste repositório contém o projeto prático produzido para a disciplina MATA88 - Fundamentos de Sistemas Distribuídos na Universidade Federal da Bahia (UFBA), ministrada pelo professor Raimundo José de Araújo Macêdo. O trabalho consiste em desenvolver uma aplicação distribuída em ambiente assíncrono que implemente o protocolo _Reliable Multicast_ entre processos e associe a cada mensagem entregue o valor do Relógio de _Lamport_.

## Grupo
 - David Lima
 - Mateus Seabra
 - Breno Cupertino
 - Otávio Novais
 
## Execução do código

``` sh
$ python3 ./main.py
```

Alternativamente, Abra diferentes terminais, executando em cada um o comando

``` sh
$ python3 ./initialize_client.py
```

Para entrar numa interface de linha de comando (CLI) interativa para interagir com os outros processos. Os comandos disponíveis no CLI são:

### Comandos disponíveis no CLI
 - `quit`: Sai do CLI e interrompe a execução do código.
 
 - `send`: A partir do protocolo multicast implementado, envia uma mensagem para os processos especificados.
   - Uso: 
   `>> send <message> [('ip1', addr1),('ip2', addr2),...]`
   - Ex.: Enviar mensagem "hello-world!" para os processos de IP 0.0.0.0:12345 e 0.0.0.0:54321
   `>> send hello-world! [('0.0.0.0', 12345),('0.0.0.0', 54321)]`
   
 - `sendcrash`: A partir do protocolo multicast implementado, envia uma mensagem para os processos especificados.
   - Uso: 
   `>> sendcrash <message> <successes> [(ip1, addr1),(ip2, addr2),...]`
   - Ex.: Enviar mensagem "hello-world!" para os processos de IP 0.0.0.0:12345 e 0.0.0.0:54321 e falhar (crash) após o primeiro envio
   `>> sendcrash hello-world! 1 [('0.0.0.0', 12345),('0.0.0.0', 54321)]`

