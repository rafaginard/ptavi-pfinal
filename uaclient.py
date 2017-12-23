#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys
import time

class XMLHandler(ContentHandler):

    def __init__(self):
        self.config = {}
        self.attrDict = {"account": ["username", "passwd"],
                         "uaserver": ["ip","puerto"],
                         "rtpaudio": ["puerto"],
                         "regproxy": ["ip","puerto"],
                         "log": ["path"],
                         "audio": ["path"]}

    def startElement(self, name, attrs):

        if name in self.attrDict:
            for atribute in self.attrDict[name]:
                self.config[name + "_" + atribute] = attrs.get(atribute, "")

    def Get_Tags(self):

        return self.config

def log(action, data):
    Time_Format = time.strftime("%Y%m%d%H%M%S ",
    time.gmtime(time.time()))
    log_list = []
    new_message = data.replace("\r\n", " ")
    log_list.append(Time_Format + action + " " +
                    new_message + "\r")
    for i in log_list: print(i)

# Metodo REGISTER
def register():
    DATA = ("REGISTER sip:" + User_Name + ":5555" + " SIP/2.0\r\n" +
            "Expires: " + EXPIRES + "\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + SERVER + ":" + str(PORT), DATA)

def register_with_nonce():
    nonce = "123123212312321212123"
    DATA = ("REGISTER sip:" + User_Name + ":5555" + " SIP/2.0\r\n" +
            "Authorization: Digest response=" + nonce + "\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + SERVER + ":" + str(PORT), DATA)

# Metodo INVITE
def invite():
    DATA = ("INVITE sip:" + INVITATION + " SIP/2.0\r\n" +
            "Content-Type: application/sdp\r\n\r\n" +
            "v=0\r\no=" + User_Name + "\r\ns=misesion" +
            "\r\nt=0\r\nm=audio " + Audio_Puerto + " RTP")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + SERVER + ":" + str(PORT), DATA)

#Medtodo BYE
def bye():
    DATA = ("BYE sip:" + User_Name + ":5555" + " SIP/2.0\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + SERVER + ":" + str(PORT), DATA)

if __name__ == "__main__":

# Se parsea el fichero XML
  parser = make_parser()
  cHandler = XMLHandler()
  parser.setContentHandler(cHandler)
  parser.parse(open(sys.argv[1]))

# Cogemos la variables que necesitamos para contactar con el servidor
  SERVER = cHandler.config["uaserver_ip"]
  PORT = int(cHandler.config["uaserver_puerto"])
  User_Name = cHandler.config["account_username"]
  Audio_Puerto = cHandler.config["rtpaudio_puerto"]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((SERVER, PORT))
    print("Enviando:", User_Name)
    if sys.argv[2] == "REGISTER":
        EXPIRES = sys.argv[3]
        register()
    elif sys.argv[2] == "INVITE":
        INVITATION = sys.argv[3]
        invite()
    elif sys.argv[2] == "BYE":
        USER = sys.argv[3]
        bye()


# Recibe datos del servidor.
    data = my_socket.recv(1024)
    Recieve = data.decode('utf-8').split(" ")
    if Recieve[1] == "200":
        log("Recieved from " + INVITATION + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
    elif Recieve[1] == "100":
        log("Recieved from " + INVITATION + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
        my_socket.connect((SERVER, PORT))
        DATA = ("REGISTER sip:" + User_Name + "@" + SERVER +
                " SIP/2.0" + "\r\n\r\n")
        my_socket.send(bytes(DATA, "utf-8"))
        log("Sent to " + SERVER + ":" + str(PORT), DATA)
    elif Recieve[1] == "401":
        log("Recieved from " + INVITATION + ":5555", data.decode('utf-8'))
        my_socket.connect((SERVER, PORT))
        register_with_nonce()
    else:
        log("Recieved from " + INVITATION + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
