#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socket
import sys

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



if __name__ == "__main__":

  parser = make_parser()
  cHandler = XMLHandler()
  parser.setContentHandler(cHandler)
  parser.parse(open(sys.argv[1]))

  SERVER = cHandler.config["uaserver_ip"]
  PORT = int(cHandler.config["uaserver_puerto"])
  LINE = "HOLA QUE TAL"
  EXPIRES = sys.argv[3]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect((SERVER, PORT))
    print("Enviando:", LINE)
    if sys.argv[2] == "REGISTER":
        DATA = ("REGISTER sip:" + LINE + " SIP/2.0\r\nExpires: " +
                EXPIRES + "\r\n\r\n")
        my_socket.send(bytes(DATA, "utf-8"))
    data = my_socket.recv(1024)
    print('Recibido -- ', data.decode('utf-8'))

print("Socket terminado.")
