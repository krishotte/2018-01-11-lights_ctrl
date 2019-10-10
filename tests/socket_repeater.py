# esp32 socket repeater server test app

from light2 import network_conn
import socket


def exchange_comm():
    pass


def main():
    # dd
    conn = network_conn('conf.json')
    conn.connect2()

    # socket server setup
    timeout = 20
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setblocking(True)
    serversocket.settimeout(timeout)
    print('binding server socket...')
    serversocket.bind(('192.168.0.9', 8003))
    serversocket.listen(5)

    while True:
        try:
            (clientsocket, clientaddress) = serversocket.accept()
        except OSError as err:
            if err.args[0] == 110:
                print('socket timeout')
            else:
                print(err)
                raise
        else:
            print(' communicating...')
            for i in range(1000):
                a = clientsocket.recv(32)
                clientsocket.send(a)

            print('client socket closing...')
            clientsocket.close()


def main_single():
    conn = network_conn('conf.json')
    conn.connect2()

    # socket server setup
    timeout = 20
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setblocking(True)
    serversocket.settimeout(timeout)
    print('binding server socket...')
    serversocket.bind(('192.168.0.9', 8003))
    serversocket.listen(5)

    while True:
        try:
            (clientsocket, clientaddress) = serversocket.accept()
        except OSError as err:
            if err.args[0] == 110:
                print('socket timeout')
            else:
                print(err)
                raise
        else:
            print(' communicating...')
            # for i in range(1000):
            a = clientsocket.recv(16)
            clientsocket.send(a)

            print('client socket closing...')
            clientsocket.close()
