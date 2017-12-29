#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from proxy_registrar import Logger
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

        self.check = False
        user_to_send_ip = ""
        user_audio_port = ""
        line = self.rfile.read()
        print(line.decode('utf-8'))
        #logger_data.action_received()
        if line:
            self.DATA = line.decode('utf-8').split(" ")
            if self.Comprobar_Peticion():
                if self.DATA[0] == "INVITE":
                    user_to_send_ip = self.DATA[4].split("\n")[0]
                    user_audio_port = self.DATA[5]
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 200 OK\r\n")
                    self.wfile.write(sdp_message)
                elif self.DATA[0] == "BYE":
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "ACK":
                    aEjecutar = ("./mp32rtp -i " + user_to_send_ip +
                                " -p " + user_audio_port)
                    aEjecutar += " < " + fichero_audio
                    os.system(aEjecutar)
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
    User_Name = cHandler.config["account_username"]
    Audio_Puerto = cHandler.config["rtpaudio_puerto"]
    sdp_data = ("Content-Type: application/sdp\r\n\r\n" +
                "v=0\r\no=" + User_Name + " " + SERVER +
                "\r\ns=misesion" + "\r\nt=0\r\nm=audio " +
                Audio_Puerto + " RTP")
    sdp_message = (bytes(sdp_data, "utf-8"))
    fichero_audio = cHandler.config["audio_path"]
    file_log = cHandler.config["log_path"]
    logger_data =  Logger()


    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((SERVER, PORT), EchoHandler)
    try:
        logger_data.start_log()
        print("Listening...")
        serv.serve_forever()
    except KeyboardInterrupt:
        logger_data.finish_log()
        sys.exit("Usage: python3 server.py IP port audio_file")
