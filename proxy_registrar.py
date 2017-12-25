#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import json
import socketserver
import sys
import time

class XMLHandler(ContentHandler):

    def __init__(self):
        self.config = {}
        self.attrDict = {"server": ["name", "ip", "puerto"],
                         "database": ["path","passwdpath"],
                         "log": ["path"]}

    def startElement(self, name, attrs):

        if name in self.attrDict:
            for atribute in self.attrDict[name]:
                self.config[name + "_" + atribute] = attrs.get(atribute, "")

    def Get_Tags(self):
        return self.config

class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    dicc_Data = {}

    def check_server(self):
        """
        Comprueba los usuarios caducados
        """
        dicc_Temp = {}
        Time_Format = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(time.time()))
        if self.dicc_Data:
            for user in self.dicc_Data:
                tiempo = self.dicc_Data[user][3]
                dicc_Temp[user] = tiempo[9:]
            for user in dicc_Temp:
                if dicc_Temp[user] < Time_Format:
                    del self.dicc_Data[user]

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """
        Time_Format = time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.gmtime(time.time()))
        nonce = b"898989898798989898989"
        DATA = []
        self.check_server()
        for line in self.rfile:
            DATA.append(line.decode('utf-8'))
        DATA = "".join(DATA).split()
        user = DATA[1].split(":")

        if DATA[0] == "REGISTER":
            if user[1] in self.dicc_Data:
                tiempo_exp = float(DATA[4]) + time.time()
                tiempo_exp = time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.gmtime(tiempo_exp))
                print(" ".join(DATA), "\r\n\r\n")
                self.dicc_Data[user[1]] = (self.client_address[0],
                                           self.client_address[1],
                                           "Time Register: " + Time_Format,
                                           "Expires: " + tiempo_exp)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            else:
                if len(DATA) == 5:
                    if int(DATA[4]) == 0:
                        try:
                            print("Usuario borrado:", user[1], "\r\n\r\n")
                            del self.dicc_Data[user[1]]
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        except KeyError:
                            self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                    elif int(DATA[4]) >= 0:
                        print(" ".join(DATA), "\r\n\r\n")
                        self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n")
                        self.wfile.write(b"WWW Authenticate:" +
                                         b"Digest nonce=" + nonce)
                        self.wfile.write(b"\r\n\r\n")
                elif len(DATA) == 8:
                    tiempo_exp = float(DATA[4]) + time.time()
                    tiempo_exp = time.strftime("%Y-%m-%d %H:%M:%S",
                                               time.gmtime(tiempo_exp))
                    print(" ".join(DATA), "\r\n\r\n")
                    self.dicc_Data[user[1]] = (self.client_address[0],
                                               self.client_address[1],
                                               "Time Register: " + Time_Format,
                                               "Expires: " + tiempo_exp)
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

            print(self.dicc_Data)
if __name__ == "__main__":
    # Listens at localhost ('') port 6001
    # and calls the EchoHandler class to manage the request
    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(sys.argv[1]))

    if cHandler.config["server_ip"] == "":
        SERVER = "127.0.0.1"
    else:
        SERVER = cHandler.config["server_ip"]
    PORT = int(cHandler.config["server_puerto"])
    serv = socketserver.UDPServer((SERVER, PORT), SIPRegisterHandler)

    print("Server " + cHandler.config["server_name"] +
          " listening at port " + str(PORT) + "...")
    serv.serve_forever()
