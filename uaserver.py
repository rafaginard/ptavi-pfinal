#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os
import socketserver
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

class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    dicc_Data = {}

    def Comprobar_Peticion(self):
        if len(self.DATA) >= 3:
            condition_sip = self.DATA[1].split(":")[0] == ("sip")
            #condition_final = self.DATA[2] == ("SIP/2.0\r\n")
            condition_arroba = False
            if self.DATA[1].find("@") != -1:
                condition_arroba = True
            if condition_sip and condition_arroba:
                self.check = True
        return self.check


    def handle(self):
        nonce = b"898989898798989898989"
        self.check = False
        line = self.rfile.read()
        print(line.decode('utf-8'))
        if line:
            self.DATA = line.decode('utf-8').split(" ")

            if self.Comprobar_Peticion():
                if self.DATA[0] == "REGISTER":
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n")
                    self.wfile.write(b"WWW Authenticate:" +
                                     b"Digest nonce=" + nonce)
                    self.wfile.write(b"\r\n\r\n")
                    #AÑADIR AL DICCIONARIO
                elif self.DATA[0] == "INVITE":
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "BYE":
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "ACK":
                    self.wfile.write(b"RECIBIDO")
                elif self.DATA[0] != ("INVITE" or "ACK" or "BYE"):
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
        if not line:
            pass

if __name__ == "__main__":

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))

    SERVER = cHandler.config["uaserver_ip"]
    PORT = int(cHandler.config["uaserver_puerto"])

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((SERVER, PORT), EchoHandler)
    try:
        print("Listening...")
        serv.serve_forever()
    except:
        sys.exit("Usage: python3 server.py IP port audio_file")
