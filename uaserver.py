#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import os
import socketserver
import sys


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def Comprobar_Peticion(self):
        if len(self.DATA) == 3:
            condition_sip = self.DATA[1].split(":")[0] == ("sip")
            condition_final = self.DATA[2] == ("SIP/2.0\r\n\r\n")
            condition_arroba = False
            if self.DATA[1].find("@") != -1:
                condition_arroba = True
            if condition_sip and condition_arroba and condition_final:
                self.check = True
        return self.check

    def handle(self):
        self.check = False
        line = self.rfile.read()
        print(line.decode('utf-8'))
        if line:
            self.DATA = line.decode('utf-8').split(" ")

            if self.Comprobar_Peticion():
                if self.DATA[0] == "REGISTER":
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "INVITE":
                    self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "BYE":
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif self.DATA[0] == "ACK":
                    audio = sys.argv[3]
                    aEjecutar = "mp32rtp -i 127.0.0.1 -p 23032 < " + audio
                    os.system(aEjecutar)
                elif self.DATA[0] != ("INVITE" or "ACK" or "BYE"):
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
        if not line:
            pass

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(("", 5555), EchoHandler)
    try:
        print("Listening...")
        serv.serve_forever()
    except:
        sys.exit("Usage: python3 server.py IP port audio_file")
