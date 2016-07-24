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

    def put(self, src, dst, recursive=False):
        self.__scp.put(src, dst, recursive)

    def get(self, src, dst, recursive=False):
        self.__scp.get(src, dst, recursive)

    def __del__(self):
        self.__scp.close()
        self.__ssh_client.close()


def get_current_dir():
    cp = subprocess.run(["pwd"], stdout = subprocess.PIPE)
    return cp.stdout

drivers_local = '/home/max/development'
nvt_dir_local = '/home/max/development/nvt'
nvt_dir_make = '/home/sukhanov/nvt/'
nvt_ver = '1.0.18'
nvt_pack = 'nvt-{}.tar.gz'.format(nvt_ver)

nvt_server_hostname = '192.168.24.106'
nvt_server_user = 'root'
make_server_hostname = '192.168.204.32'
make_server_user = 'sukhanov'


# nvt_server = host(nvt_server_hostname, nvt_server_user)
# make_server = host(make_server_hostname, make_server_user)


current_dir = get_current_dir()

# создание tar.gz
subprocess.run(["cd", nvt_dir_local])
subprocess.run(["make", "package_source"])

# загрузка на сборочный сервер
make_server.put(nvt_pack, nvt_dir_make)

# сборка на сборочном сервере
make_server.exec_command("cd " + nvt_dir_make)
make_server.exec_command("tar xvzf " + nvt_pack)
make_server.exec_command("rm -f " + nvt_pack)
make_server.exec_command("cd nvt-" + nvt_ver)
make_server.exec_command("mkdir build")
make_server.exec_command("cd build")
make_server.exec_command("cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_MYSQL=1")
make_server.exec_command("make -j4")

# загрузка библиотеки с драйверами со сборочного сервера
make_server.get(nvt_dir_make + "nvt-" + nvt_ver + "/build/bin/drivers/libnvtd_drivers.so", drivers_local)
