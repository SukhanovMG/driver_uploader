#! /bin/env python

import subprocess
import os
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

    def put(self, src, dst, recursive=False):
        self.__scp.put(src, dst, recursive)

    def get(self, src, dst, recursive=False):
        self.__scp.get(src, dst, recursive)

    def __del__(self):
        self.__scp.close()
        self.__ssh_client.close()

drivers_local = '/home/max/development'
nvt_dir_local = '/home/max/development/nvt'
nvt_dir_local_build = nvt_dir_local + '/build'
nvt_dir_make = '/home/sukhanov/nvt/'
nvt_ver = '1.0.17'
nvt_pack = 'nvt-{}.tar.gz'.format(nvt_ver)

nvt_server_hostname = '192.168.24.106'
nvt_server_user = 'root'
make_server_hostname = '192.168.204.32'
make_server_user = 'sukhanov'


#nvt_server = host(nvt_server_hostname, nvt_server_user)
make_server = host(make_server_hostname, make_server_user)


current_dir = os.getcwd()

# создание tar.gz
os.chdir(nvt_dir_local_build)
subprocess.run(["make package_source"], shell=True)

# загрузка на сборочный сервер
make_server.put(nvt_dir_local_build + '/' + nvt_pack, nvt_dir_make)

# сборка на сборочном сервере
cmd = "cd {0} && tar xvzf {1} && rm -f {1} && cd nvt-{2} && mkdir build && cd build && cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_MYSQL=1 && make -j4".format(nvt_dir_make, nvt_pack, nvt_ver)
make_server.exec_cmd(cmd)

# загрузка библиотеки с драйверами со сборочного сервера
make_server.get(nvt_dir_make + "nvt-" + nvt_ver + "/build/bin/drivers/libnvtd_drivers.so", drivers_local)
