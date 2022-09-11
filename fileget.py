#!/usr/bin/env python3.8
#Jozef Makiš (xmakis00)

import socket
import argparse
import sys
import os
import re

def udp_connection (part1, part2, server_name_par):
    try:
        msg = "WHEREIS " + server_name_par + "\r\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        try:
            socket.inet_aton(part1)
        except socket.error:
            sys.exit("Socket Error")
        s.settimeout(20.0)
        s.connect((part1, part2))
        s.sendall(msg.encode())
        data = s.recv(4096)
    except Exception:
        sys.exit("Spojenie UDP zlyhalo!")
    if data[:2].decode() != "OK":
        sys.exit("Nepodarilo sa nadviazat UDP spojenie.")
    return data[3:].decode()

def tcp_connection (part1, part2, subor, meno_domeny):
    for temp_subor in subor:
        try:
            msg = "GET " + temp_subor + " FSP/1.0\r\nHostname: " + meno_domeny + "\r\nAgent: xmakis00\r\n\r\n"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                socket.inet_aton(part1)
            except socket.error:
                sys.exit("Socket Error")
            s.settimeout(20.0)
            s.connect((part1, part2))
            s.sendall((msg.encode()))
            filecontent = b''
            while True:
                data = s.recv(4096)
                if not data: break
                filecontent += data
        except Exception:
            sys.exit("Spojenie TCP zlyhalo!")

        if filecontent[:15] != b"FSP/1.0 Success":
            sys.exit("Nespravna odpoved zo servera.")

        filecontent_without_header = filecontent.split(b'\r\n\r\n')

        if re.findall('/', temp_subor):
            os.makedirs(os.path.dirname(temp_subor), exist_ok=True)
        f = open(temp_subor, 'wb')
        for x_iter in range(1, len(filecontent_without_header)):
            f.write(filecontent_without_header[x_iter])
        f.close()


def index_download (part1, part2, meno_domeny):
    try:
        msg = "GET " + 'index' + " FSP/1.0\r\nHostname: " + meno_domeny + "\r\nAgent: xmakis00\r\n\r\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(20.0)
        s.connect((part1, part2))
        s.sendall((msg.encode()))
        filecontent = b''
        while True:
            data = s.recv(4096)
            if not data: break
            filecontent += data
    except Exception:
        sys.exit("Spojenie TCP zlyhalo!")

    if filecontent[:15] != b"FSP/1.0 Success":
        sys.exit("Nespravna odpoved zo servera.")

    filecontent_without_header = filecontent.split(b'\r\n\r\n')

    if re.findall('/', 'index'):
        os.makedirs(os.path.dirname('index'), exist_ok=True)
    f = open('index', 'wb')
    for x_iter in range(1, len(filecontent_without_header)):
        f.write(filecontent_without_header[x_iter])
    f.close()

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-n", type=str, dest="IP_adres")
parser.add_argument("-f", type=str, dest="SURL")
args = parser.parse_args()

if args.IP_adres is None or args.SURL is None:
    sys.exit("Chybné argumenty.")

ip_part = args.IP_adres.split(":")
try:
    args.SURL = args.SURL[6:]
except Exception:
    sys.exit("Nespravny tvar SURL.")

server_name = args.SURL.split("/")

arr_len = len(server_name)
filepath = ''
arr_files = [0 for i in range(1)]
try:
    arr_files[0] = server_name[1]
except Exception:
    sys.exit("Nesprany nazov serveru")

try:
    port = int(ip_part[1])
except Exception:
    sys.exit("Nespravny format adresy.")

if arr_len > 2:
    for x in range(arr_len):
        if x != 0:
            filepath = filepath  + server_name[x]
            if x != arr_len - 1:
                filepath += '/'
    server_name[1] = filepath

udp_result = udp_connection(ip_part[0], int(ip_part[1]), server_name[0])
udp_result = udp_result.split(":")
hromadny_download = False
if server_name[1] == '*':
    try:
        hromadny_download = True
        index_download(udp_result[0], int(udp_result[1]), server_name[0])
        f_index = open('index', 'r')
        arr_files = f_index.read().splitlines()
    except Exception:
        sys.exit("Pre stiahnutie celého adresára je potrebné najprv stiahnuť index")

tcp_connection(udp_result[0], int(udp_result[1]), arr_files, server_name[0])
