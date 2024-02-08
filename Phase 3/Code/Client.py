import socket
import json
import GetData
from Pyxcel import number_to_string
from copy import deepcopy
import time


HEADER = 64
PORT = 6846
SERVER = "192.168.1.103"
ADDR = ("localhost", PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def edit(table):
    table.pop(0)
    for i in range(len(table)):
        table[i].pop(0)
    return table

def run():
    send("create(data, 6, 15007)")
    send("context(data)")

    setHeader = ['A1 = Company',
                 'B1 = Car',
                 'C1 = Tream',
                 'D1 = Kilometer',
                 'E1 = Year',
                 'F1 = Price']
    for i in setHeader:
        send(i)

    Columns = ["company", "car", "tream", "kilometer", "year", "price"]
    Data = GetData.run()
    r, c = 2, 0
    for dic in Data:
        for i in Columns:
            send(f"{number_to_string(c)}{r} = {dic[i]}")
            c += 1
        r += 1
        c = 0
    
    send("!DISCONNECT")
    tbl = []
    #time.sleep(20)
    connected = True
    while connected:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                break
            msg = json.loads(msg)
            #print(msg)
            tbl = tbl + deepcopy(msg)

    return tbl