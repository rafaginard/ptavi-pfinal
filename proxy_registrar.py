#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import json
import socketserver
import socket
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

    def invite(self, DATA):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            user_to_send = DATA[1].split(":")[1]
            user_who_invites = DATA[6].split("=")[1]
            user_who_invites_ip = DATA[7]
            audio_port = DATA[11]
        #try:
            user_to_send_ip = self.dicc_Data.get(user_to_send)[0]
            user_to_send_port = self.dicc_Data.get(user_to_send)[1]
            my_socket.connect((user_to_send_ip, int(user_to_send_port)))
            Invitation = ("INVITE sip:" + user_to_send + " SIP/2.0\r\n" +
                          "Content-Type: application/sdp\r\n\r\n" +
                          "v=0\r\no=" + user_who_invites + " " +
                          user_who_invites_ip + "\r\ns=misesion" +
                          "\r\nt=0\r\nm=audio " + audio_port + " RTP")
            my_socket.send(bytes(Invitation, "utf-8"))
            print(Invitation)
        #except TypeError:
        #    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")

            data = my_socket.recv(1024)
            Recieve = data.decode('utf-8').split(" ")
            #audio_port = Recieve[16]
            print(Recieve)
            sdp_data = ("Content-Type: application/sdp\r\n\r\n" +
                             "v=0\r\no=" + user_to_send + " " +
                             user_to_send_ip + "\r\ns=misesion" +
                             "\r\nt=0\r\nm=audio " + audio_port + " RTP")
            sdp_message = (bytes(sdp_data, "utf-8"))
            if Recieve[1] ==  "100":
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n" + sdp_message)




    def ack(self, DATA):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            user_to_send = DATA[1].split(":")[1]
            user_to_send_ip = self.dicc_Data.get(user_to_send)[0]
            user_to_send_port = self.dicc_Data.get(user_to_send)[1]
            my_socket.connect((user_to_send_ip, int(user_to_send_port)))
            Response = ("ACK sip:" + user_to_send +
                        " SIP/2.0\r\n\r\n")
            my_socket.send(bytes(Response, "utf-8"))
            print(Response)

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
        print(DATA)
        if DATA[0] == "REGISTER":
            user = DATA[1].split(":")[1]
            port = DATA[1].split(":")[2]
            if user in self.dicc_Data:
                tiempo_exp = float(DATA[4]) + time.time()
                tiempo_exp = time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.gmtime(tiempo_exp))
                print(" ".join(DATA), "\r\n\r\n")
                self.dicc_Data[user] = (self.client_address[0],
                                           self.client_address[1],
                                           "Time Register: " + Time_Format,
                                           "Expires: " + tiempo_exp)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            else:
                if len(DATA) == 5:
                    if int(DATA[4]) == 0:
                        try:
                            print("Usuario borrado:", user, "\r\n\r\n")
                            del self.dicc_Data[user]
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
                    self.dicc_Data[user] = (self.client_address[0],
                                            port,
                                            "Time Register: " + Time_Format,
                                            "Expires: " + tiempo_exp)
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif DATA[0] == "INVITE":
            self.invite(DATA)
        elif DATA[0] == "ACK":
            self.ack(DATA)


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
