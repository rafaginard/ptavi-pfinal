#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import json
import socket
import sys
import time
import os

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
    with open("log.txt", "w") as data_file:
        data_file.write(" ".join(log_list))

def send_mp3():

    aEjecutar = ("./mp32rtp -i " + user_to_send_ip +
                " -p " + user_audio_port)
    aEjecutar += " < " + fichero_audio
    os.system(aEjecutar)
    log("Sent to " + user_to_send_ip + ":" + str(user_audio_port), DATA)
# Metodo REGISTER
def register():

    DATA = ("REGISTER sip:" + User_Name + ":" + str(Port) + " SIP/2.0\r\n" +
            "Expires: " + EXPIRES + "\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + Proxy_Ip + ":" + str(Proxy_Port), DATA)

def register_with_nonce():

    nonce = "123123212312321212123"
    DATA = ("REGISTER sip:" + User_Name + ":" + str(Port) + " SIP/2.0\r\n" +
            "Expires: " + EXPIRES + "\r\n\r\n" +
            "Authorization: Digest response=" + nonce + "\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + Proxy_Ip + ":" + str(Proxy_Port), DATA)
# Metodo INVITE
def invite():

    DATA = ("INVITE sip:" + Invitation + " SIP/2.0\r\n" +
            "Content-Type: application/sdp\r\n\r\n" +
            "v=0\r\no=" + User_Name + " " + Server + "\r\ns=misesion" +
            "\r\nt=0\r\nm=audio " + Audio_Puerto + " RTP")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + Server + ":" + str(Port), DATA)

# Metodo ACK
def ack():

    DATA = ("ACK sip:" + Invitation + " SIP/2.0\r\n\r\n" )
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + Server + ":" + str(Port), DATA)

#Medtodo BYE
def bye():

    DATA = ("BYE sip:" + user_to_send + " SIP/2.0\r\n\r\n")
    my_socket.send(bytes(DATA, "utf-8"))
    log("Sent to " + Server + ":" + str(Port), DATA)
    data = my_socket.recv(1024)
    Recieve = data.decode('utf-8').split(" ")
    print(data.decode("utf-8"))

if __name__ == "__main__":

# Se parsea el fichero XML
  parser = make_parser()
  cHandler = XMLHandler()
  parser.setContentHandler(cHandler)
  parser.parse(open(sys.argv[1]))

# Cogemos la variables que necesitamos para contactar con el servidor
  Server = cHandler.config["uaserver_ip"]
  Port = int(cHandler.config["uaserver_puerto"])
  User_Name = cHandler.config["account_username"]
  Audio_Puerto = cHandler.config["rtpaudio_puerto"]
  fichero_audio = cHandler.config["audio_path"]
  file_log = cHandler.config["log_path"]

  if cHandler.config["regproxy_ip"] == "":
      Proxy_Ip = "127.0.0.1"
  else:
      Proxy_Ip = cHandler.config["regproxy_ip"]
  Proxy_Port = int(cHandler.config["regproxy_puerto"])

  log("Starting...", " ")
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    print("Enviando:", User_Name)
    if sys.argv[2] == "REGISTER":
        my_socket.connect((Proxy_Ip, Proxy_Port))
        Invitation = Proxy_Ip
        EXPIRES = sys.argv[3]
        register()
    elif sys.argv[2] == "INVITE":
        my_socket.connect((Proxy_Ip, Proxy_Port))
        Invitation = sys.argv[3]
        invite()
    elif sys.argv[2] == "BYE":
        my_socket.connect((Proxy_Ip, Proxy_Port))
        user_to_send = sys.argv[3]
        bye()

# Recibe datos del servidor.
    data = my_socket.recv(1024)
    Recieve = data.decode('utf-8').split(" ")
    #print(Recieve)
    if Recieve[1] == "200":
        log("Recieved from " + Invitation + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
    elif Recieve[1] == "100":
        log("Recieved from " + Invitation + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
        user_to_send = Recieve[7].split("=")[2]
        user_to_send_ip = Recieve[8].split("\r\n")[0]
        user_audio_port = Recieve[9]
        my_socket.connect((Proxy_Ip, Proxy_Port))
        ack()
        send_mp3()
        bye()
        data = my_socket.recv(1024)
        print(data.decode("utf-8"))
    elif Recieve[1] == "401":
        log("Recieved from " + Proxy_Ip + ":" + str(Proxy_Port),
            data.decode('utf-8'))
        my_socket.connect((Proxy_Ip, Proxy_Port))
        register_with_nonce()
        data = my_socket.recv(1024)
        print(data.decode('utf-8'))
    else:
        log("Recieved from " + Invitation + ":5555", data.decode('utf-8'))
        print(data.decode('utf-8'))
