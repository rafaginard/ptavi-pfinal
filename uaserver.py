#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from proxy_registrar import Logger, SIPRegisterHandler
import os
import socketserver
import sys


class XMLHandler(ContentHandler):

    def __init__(self):
        self.config = {}
        self.attrDict = {"account": ["username", "passwd"],
                         "uaserver": ["ip", "puerto"],
                         "rtpaudio": ["puerto"],
                         "regproxy": ["ip", "puerto"],
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
    rtp_data = {}

    def Comprobar_Peticion(self, DATA):
        check = False
        if len(DATA) >= 3:
            condition_sip = DATA[1].split(":")[0] == ("sip")
            condition_arroba = False
            if DATA[1].find("@") != -1:
                condition_arroba = True
            if condition_sip and condition_arroba:
                check = True
        return check

    def handle(self):

        line = self.rfile.read()
        print(line.decode('utf-8'))
        logger_data.action_received(Proxy_Ip, Proxy_Port, line.decode("utf-8"))
        if line:
            DATA = line.decode('utf-8').split(" ")
            # print(DATA)
            if self.Comprobar_Peticion(DATA):
                if DATA[0] == "INVITE":
                    self.rtp_data["1"] = [DATA[4].split("\r\n")[0], DATA[5]]
                    print(self.rtp_data["1"][0])
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    Message = "SIP/2.0 100 Trying\r\n\r\n"
                    logger_data.action_send(Proxy_Ip, Proxy_Port, Message)
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    Message = "SIP/2.0 180 Ringing\r\n\r\n"
                    logger_data.action_send(Proxy_Ip, Proxy_Port, Message)
                    self.wfile.write(b"SIP/2.0 200 OK\r\n")
                    self.wfile.write(sdp_message)
                    s = sdp_message.decode("utf-8")
                    Message = "SIP/2.0 200 OK\r\n" + s
                    logger_data.action_send(Proxy_Ip, Proxy_Port, Message)
                elif DATA[0] == "BYE":
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    Message = "SIP/2.0 200 OK\r\n\r\n"
                    logger_data.action_send(Proxy_Ip, Proxy_Port, Message)
                elif DATA[0] == "ACK":
                    aEjecutar = ("./mp32rtp -i " + self.rtp_data["1"][0] +
                                 " -p " + self.rtp_data["1"][1])
                    aEjecutar += " < " + fichero_audio
                    os.system(aEjecutar)
                    Message = "Enviando datos"
                    logger_data.action_send(Proxy_Ip, Proxy_Port, Message)
                elif DATA[0] != ("INVITE" or "ACK" or "BYE"):
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
                    Message = "SIP/2.0 405 Method Not Allowed"
                    logger_data.action_error(Message)
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                Message = "SIP/2.0 400 Bad Request"
                logger_data.action_error(Message)
        if not line:
            pass

if __name__ == "__main__":

    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    try:
        parser.parse(open(sys.argv[1]))
    except (IndexError, FileNotFoundError):
        sys.exit("Usage: python uaserver.py config")

    SERVER = cHandler.config["uaserver_ip"]
    PORT = int(cHandler.config["uaserver_puerto"])
    if cHandler.config["regproxy_ip"] == "":
        Proxy_Ip = "127.0.0.1"
    else:
        Proxy_Ip = cHandler.config["regproxy_ip"]
    Proxy_Port = int(cHandler.config["regproxy_puerto"])
    User_Name = cHandler.config["account_username"]
    Audio_Puerto = cHandler.config["rtpaudio_puerto"]
    sdp_data = ("Content-Type: application/sdp\r\n\r\n" +
                "v=0\r\no=" + User_Name + " " + SERVER +
                "\r\ns=misesion" + "\r\nt=0\r\nm=audio " +
                Audio_Puerto + " RTP")
    sdp_message = (bytes(sdp_data, "utf-8"))
    fichero_audio = cHandler.config["audio_path"]
    file_log = cHandler.config["log_path"]
    logger_data = Logger()

    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((SERVER, PORT), EchoHandler)
    try:
        logger_data.start_log()
        print("Listening...")
        serv.serve_forever()
    except KeyboardInterrupt:
        logger_data.finish_log()
