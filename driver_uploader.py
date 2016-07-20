#! /bin/env python

import subprocess
import getpass
import paramiko
import scp

class host:
    def __init__(self, hostname, user, pwd=None, port=22):
        self.__hostname = hostname
        self.__user = user
        if not pwd:
            promt = 'Enter password for {0}@{1}:'
            self.__pwd = getpass.getpass(promt.format(self.__user, self.__hostname))
        else:
            self.__pwd = pwd               

        self.__port = port

        # ssh
        self.__ssh_client = paramiko.SSHClient()
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__ssh_client.connect(hostname = self.__hostname, username = self.__user, password = self.__pwd, port = self.__port)

        # file transfer
        self.__scp = scp.SCPClient(self.__ssh_client.get_transport())

    def exec_cmd(self, cmd):
        if type(cmd) is str:
            stdin, stdout, stderr = self.__ssh_client.exec_command(cmd)
            print('==========')
            print(cmd)
            print('==STDOUT==')
            print(stdout.read())
            print('==STDERR==')
            print(stderr.read())
            print('==========')

    def send_file(self, src, dst):
        self.__scp.put(src, dst)


    def __del__(self):
        self.__scp.close()
        self.__ssh_client.close()


nvt_dir = '/home/max/development/nvt'

nvt_server_hostname = '192.168.24.106'
nvt_server_user = 'root'
make_server_hostname = '192.168.204.32'
make_server_user = 'sukhanov'


nvt_server = host(nvt_server_hostname, nvt_server_user)
make_server = host(make_server_hostname, make_server_user)

#make_server.exec_cmd('ls -l')
#make_server.send_file('scp.py', '~/scp.py')

current_dir = 