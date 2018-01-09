#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa principal de un Proxy_Registrar
"""

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
import json
import socketserver
import socket
import sys
import time


class Logger():

    def __init__(self):
        from __main__ import file_log as log
        self.log = log

    def get_time(self):
        Time_Format = time.strftime("%Y%m%d%H%M%S ", time.gmtime(time.time()))
        return Time_Format

    def write_in_log(self, action):
        with open(self.log, "a") as data_log:
            data_log.write(action)

    def read_from_log(self):
        file = open(self.log, "r")
        print(file.read())

    def start_log(self):
        actual_time = self.get_time()
        action = (actual_time + "Starting...")
        self.write_in_log(action + "\r")

    def finish_log(self):
        actual_time = self.get_time()
        action = (actual_time + "Finishing...")
        self.write_in_log(action + "\r")

    def action_send(self, Ip_send, Port_send, Message):
        actual_time = self.get_time()
        action = (actual_time + "Send to " +
                  Ip_send + ":" + str(Port_send) + ": " +
                  Message.replace("\r\n", " "))
        self.write_in_log(action + "\r")

    def action_received(self, Ip_recv, Port_recv, Message):
        actual_time = self.get_time()
        action = (actual_time + "Received from " +
                  Ip_recv + ":" + str(Port_recv) + ": " +
                  Message.replace("\r\n", " "))
        self.write_in_log(action + "\r")

    def action_error(self, Ip, Port, Message):
        actual_time = self.get_time()
        action = (actual_time + Message + Ip + " port " + str(Port))
        self.write_in_log(action + "\r")


class XMLHandler(ContentHandler):

    def __init__(self):
        self.config = {}
        self.attrDict = {"server": ["name", "ip", "puerto"],
                         "database": ["path", "passwdpath"],
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
    passwd_data = {}

    def read_passwd(self):

        with open(passwd_database, "r") as data_file:
            for line in data_file:
                key = line.split(" ")[0]
                value = line.split(" ")[1]
                self.passwd_data[key] = value

    def update_database(self):
        """
        Convierte mi biblioteca de datos a un archivo json
        """
        with open(database, "w") as data_file:
            for k, v in self.dicc_Data.items():
                data_file.write(str(k) + "---> " +
                                str(v) + "\r")

    def read_database(self):
        """
        Recoge los datos del archivo json (si existe) y los
        vuelca en mi diccioario de datos
        """
        try:
            with open(database, "r") as data_file:
                for line in data_file:
                    key = line.split("--->")[0]
                    Values = line.split("--->")[1]
                    V = Values.split(",")
                    ip = V[0].split("(")[1]
                    port = V[1]
                    time_register = V[2]
                    time_expired = V[3].split(")")[0]
                    self.dicc_Data[key] = (ip, port, float(time_register),
                                           float(time_expired))
        except (NameError, FileNotFoundError):
            pass

    def check_passwd(self, user, nonce):

        contra = self.passwd_data[user]
        h = hashlib.sha1(bytes(contra, "utf-8"))
        h.update(bytes(nonce, "utf-8"))
        return h.hexdigest()

    def check_server(self):
        """
        Comprueba los usuarios caducados
        """
        dicc_Temp = {}
        Time_Format = time.time()
        if self.dicc_Data:
            for user in self.dicc_Data:
                tiempo = self.dicc_Data[user][3]
                dicc_Temp[user] = tiempo
            for user in dicc_Temp:
                if dicc_Temp[user] < Time_Format:
                    del self.dicc_Data[user]
            self.update_database()

    def register(self, DATA):
        nonce = "89898347853"
        Time_Format = time.time()

        self.read_passwd()
        ip = self.client_address[0]
        user = DATA[1].split(":")[1]
        port = DATA[1].split(":")[2]
        proxy_log.action_received(ip, port, " ".join(DATA))
        if user in self.dicc_Data:
            tiempo_exp = float(DATA[4]) + time.time()
            # tiempo_exp = time.strftime("%Y-%m-%d %H:%M:%S",
            #                           time.gmtime(tiempo_exp))
            print(" ".join(DATA), "\r\n\r\n")
            self.dicc_Data[user] = (ip, port,
                                    Time_Format,
                                    tiempo_exp)
            self.update_database()
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        else:
            if len(DATA) == 5:
                if int(DATA[4]) == 0:
                    try:
                        print("Usuario borrado:", user, "\r\n\r\n")
                        del self.dicc_Data[user]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        proxy_log.action_send(ip, port, "SIP/2.0 200 OK")
                        self.update_database()
                    except KeyError:
                        self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                        Message = "SIP/2.0 404 User Not FOund"
                        proxy_log.action_send(ip, port, Message)
                elif int(DATA[4]) >= 0:
                    print(" ".join(DATA), "\r\n\r\n")
                    Response = ("SIP/2.0 401 Unauthorized\r\n" +
                                "WWW-Authenticate:" + 'Digest nonce="' +
                                nonce + '"' + "\r\n\r\n")

                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n")
                    self.wfile.write(b"WWW-Authenticate:" +
                                     b'Digest nonce="' + bytes(nonce, "utf-8") +
                                     b'"')
                    self.wfile.write(b"\r\n\r\n")
                    proxy_log.action_send(ip, port, Response)
            elif len(DATA) == 8:
                client_digest = DATA[7].split("=")[1]
                tiempo_exp = float(DATA[4]) + time.time()
                # tiempo_exp = time.strftime("%Y-%m-%d %H:%M:%S",
                #                           time.gmtime(tiempo_exp))
                print(" ".join(DATA), "\r\n\r\n")
                digest = self.check_passwd(user, nonce)
                if digest == client_digest:
                    self.dicc_Data[user] = (self.client_address[0],
                                            port,
                                            Time_Format,
                                            tiempo_exp)
                    self.update_database()
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    proxy_log.action_received(ip, port, " ".join(DATA))
                else:
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n\r\n")

    def invite(self, DATA):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            try:
                _to_send = DATA[1].split(":")[1]
                _who_invites = DATA[6].split("=")[1]
                _who_invites_ip = DATA[7]
                _who_invites_port = self.dicc_Data.get(_who_invites)[1]
                audio_port = DATA[11]
                proxy_log.action_received(_who_invites_ip, _who_invites_port, " ".join(DATA))

                _to_send_ip = self.dicc_Data.get(_to_send)[0]
                _to_send_port = self.dicc_Data.get(_to_send)[1]
                my_socket.connect((_to_send_ip, int(_to_send_port)))
                Invitation = ("INVITE sip:" + _to_send + " SIP/2.0\r\n" +
                              "Content-Type: application/sdp\r\n\r\n" +
                              "v=0\r\no=" + _who_invites + " " +
                              _who_invites_ip + "\r\ns=misesion" +
                              "\r\nt=0\r\nm=audio " + audio_port + " RTP")
                my_socket.send(bytes(Invitation, "utf-8"))
                proxy_log.action_send(_to_send_ip, _to_send_port, Invitation)
                print(Invitation)

                data = my_socket.recv(1024)
                new_data = data.decode("utf-8")
                Recieve = data.decode('utf-8').split(" ")
                proxy_log.action_received(_to_send_ip, _to_send_port, new_data)
                # print(Recieve)

                print(data.decode("utf-8"))
                if Recieve[1] == "100":
                    self.wfile.write(data)
            except (TypeError, ConnectionRefusedError):
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                action = "No server listening at "
                proxy_log.action_error(_to_send_ip, _to_send_port, action)

    def ack(self, DATA):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            _to_send = DATA[1].split(":")[1]
            _to_send_ip = self.dicc_Data.get(_to_send)[0]
            _to_send_port = self.dicc_Data.get(_to_send)[1]
            my_socket.connect((_to_send_ip, int(_to_send_port)))
            Response = ("ACK sip:" + _to_send +
                        " SIP/2.0\r\n\r\n")
            my_socket.send(bytes(Response, "utf-8"))
            proxy_log.action_send(_to_send_ip, _to_send_port, Response)
            print(Response)

    def bye(self, DATA):

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            _to_send = DATA[1].split(":")[1]
            _to_send_ip = self.dicc_Data.get(_to_send)[0]
            _to_send_port = self.dicc_Data.get(_to_send)[1]
            my_socket.connect((_to_send_ip, int(_to_send_port)))
            Response = ("BYE sip:" + _to_send +
                        " SIP/2.0\r\n\r\n")
            my_socket.send(bytes(Response, "utf-8"))
            proxy_log.action_send(_to_send_ip, _to_send_port, Response)
            print(Response)
            data = my_socket.recv(1024)
            new_data = data.decode("utf-8")
            Recieve = data.decode('utf-8').split(" ")
            proxy_log.action_received(_to_send_ip, _to_send_port, new_data)
            self.wfile.write(data)
            print(data.decode("utf-8"))

    def Comprobar_Peticion(self, DATA):
        check = False
        if len(DATA) >= 3:
            condition_sip = DATA[1].split(":")[0] == ("sip")
            # condition_final = self.DATA[2] == ("SIP/2.0\r\n")
            condition_arroba = False
            if DATA[1].find("@") != -1:
                condition_arroba = True
            if condition_sip and condition_arroba:
                check = True
        return check

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        """

        DATA = []
        self.read_database()
        self.check_server()
        # print(self.dicc_Data)
        for line in self.rfile:
            DATA.append(line.decode('utf-8'))
        DATA = "".join(DATA).split()

        if self.Comprobar_Peticion(DATA):
            if DATA[0] == "REGISTER":
                self.register(DATA)
            elif DATA[0] == "INVITE":
                self.invite(DATA)
            elif DATA[0] == "ACK":
                self.ack(DATA)
            elif DATA[0] == "BYE":
                self.bye(DATA)
            elif DATA[0] != ("INVITE" or "ACK" or "BYE" or "REGISTER"):
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
        else:
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")

if __name__ == "__main__":
    # Listens at localhost ('') port 6001
    # and calls the EchoHandler class to manage the request
    parser = make_parser()
    cHandler = XMLHandler()
    parser.setContentHandler(cHandler)
    try:
        parser.parse(open(sys.argv[1]))
    except (IndexError, FileNotFoundError):
        sys.exit("Usage: python proxy_registrar.py config")

    file_log = cHandler.config["log_path"]
    proxy_log = Logger()
    if cHandler.config["server_ip"] == "":
        SERVER = "127.0.0.1"
    else:
        SERVER = cHandler.config["server_ip"]
    PORT = int(cHandler.config["server_puerto"])
    database = cHandler.config["database_path"]
    passwd_database = cHandler.config["database_passwdpath"]
    serv = socketserver.UDPServer((SERVER, PORT), SIPRegisterHandler)
    proxy_log.start_log()
    try:

        print("Server " + cHandler.config["server_name"] +
              " listening at port " + str(PORT) + "...")
        serv.serve_forever()
    except KeyboardInterrupt:
        proxy_log.finish_log()
