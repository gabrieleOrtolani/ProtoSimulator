import sys
import os

# Inserisci la cartella interface e src nel path per importare messages_pb2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from interface import message_pb2

import socket

HOST = "127.0.0.1"
PORT = 5000

def send_proto_example():
    msg = message_pb2.ExampleMessage()
    msg.text = "Messaggio TCP diretto"
    msg.id = 42
    data = msg.SerializeToString()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data)

def send_command():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"send ExampleMessage\n")
        risposta = s.recv(4096)
        print("Risposta comando:", risposta)

if __name__ == "__main__":
    print("Test: invio ExampleMessage serializzato direttamente")
    send_proto_example()
    print("Test: invio comando send ExampleMessage")
    send_command()