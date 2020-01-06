"""
文件传输，本地与服务器文件传输
"""

import paramiko
import uuid
from models import Host

from utils.common.security import decrypt_oralce


class Base:
    def __init__(self, addr, user, pwd, port=22):
        self.addr = addr
        self.user = user
        self.pwd = pwd
        self.port = port
        self.connections = []


class Lazyconnection(Base):
    """批量命令连接"""
    def __init__(self, addr, user, pwd, port=22):
        super().__init__(addr, user, pwd, port)

    def __enter__(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.addr, username=self.user, password=self.pwd, port=self.port)
        self.connections.append(ssh)

        return ssh

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connections.pop().close()


class LazyFileconnection(Base):
    """批量文件连接"""
    def __init__(self, addr, user, pwd, port=22):
        super().__init__(addr, user, pwd, port)

    def __enter__(self):
        transport = paramiko.Transport((self.addr, self.port))
        transport.connect(username=self.user, password=self.pwd)
        sftp = paramiko.SFTPClient.from_transport(transport)

        self.connections.append(sftp)

        return sftp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connections.pop().close()


class BatchOperation:
    """批量操作"""

    def exec_cmd(self, host_list, cmd):
        """
        批量命令
        :param host_list: 主机列表
        :param cmd: 执行命令
        :return: 命令执行结果
        """
        results_list = []  # 结果列表
        for host in host_list:
            host_obj = Host.filter(host)[0]  # 获取主机对象
            password = decrypt_oralce(host_obj.password)    # 解密
            conn = Lazyconnection(host_obj.addr, host_obj.name, password, host_obj.port)
            with conn as s:
                stdin, stdout, stderr = s.exec_command(cmd)
                stdout_result, stderr_result = stdout.read(), stderr.read()

                print(str(stdout_result, encoding='utf-8'), str(stderr.read(), encoding='utf-8'))
                if stderr_result:
                    results_list.append({host_obj.addr: str(stderr_result, encoding='utf-8')})
                else:
                    results_list.append({host_obj.addr: str(stdout_result, encoding='utf-8')})

        return results_list

    def get(self, local_path, remote_path, host_list):
        """
        从远程主机下载文件
        :param local_path: 本地文件路径
        :param remote_path: 远程主机路径
        :param host_list: 主机列表
        :return:
        """
        for host in host_list:
            host_obj = Host.filter(host)[0]  # 获取主机对象
            password = decrypt_oralce(host_obj.password)    # 解密
            conn = LazyFileconnection(host_obj.addr, host_obj.name, password, host_obj.port)
            with conn as s:
                s.get(remote_path, local_path)  # 将remove_path 下载到本地 local_path

    def send(self, local_path, remote_path, host_list):
        """
        上传文件到远程主机
        :param local_path: 本地文件路径
        :param remote_path: 远程主机路径
        :param host_list: 主机列表
        :return:
        """
        for host in host_list:
            host_obj = Host.filter(host)[0]  # 获取主机对象
            password = decrypt_oralce(host_obj.password)    # 解密
            conn = LazyFileconnection(host_obj.addr, host_obj.name, password, host_obj.port)
            with conn as s:
                s.put(local_path, remote_path)


# class FileTransfer:
#     def __init__(self, host='192.168.40.135', port=22, username='dly', pwd='1508'):
#         self.host = host
#         self.port = port
#         self.username = username
#         self.pwd = pwd
#
#     def connect(self, host, user, pwd, port=22):
#         """连接"""
#         transport = paramiko.Transport((host, port))
#         transport.connect(username=user, password=pwd)
#         self.sftp = paramiko.SFTPClient.from_transport(transport)
#
#     def send(self, local_path, remote_path, host_list):
#         """
#         上传到服务器
#         :param local_path: 本地文件路径
#         :param remote_path: 远程服务器路径
#         :param host_list: 主机列表
#         :return:
#         """
#         for host in host_list:
#             # 从数据库中获取主机密码、端口等信息
#             host_obj = Host.filter(host)[0]  # 获取主机对象
#             self.connect(host_obj.addr, host_obj.name, host_obj.password, host_obj.port)
#
#             self.sftp.put(local_path, remote_path)
#
#     def get(self, local_path, remote_path, host_list):
#         """下载"""
#         for host in host_list:
#             # 从数据库中获取主机密码、端口等信息
#             host_obj = Host.filter(host)[0]  # 获取主机对象
#             self.connect(host_obj.addr, host_obj.name, host_obj.password, host_obj.port)
#
#             # 将remove_path 下载到本地 local_path
#             self.sftp.get(remote_path, local_path)
#
#     def batch_cmd(self, host_list, cmd):
#         """批量命令"""
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         results_list = []  # 结果列表
#
#         for host in host_list:
#             host_obj = Host.filter(host)[0]  # 获取主机对象
#             ssh.connect(hostname=host_obj.addr, port=host_obj.port, username=host_obj.name, password=host_obj.password)
#
#             # 执行命令
#             stdin, stdout, stderr = ssh.exec_command(cmd)
#             # 获取命令结果
#             result = stdout.read()
#             print(str(result, encoding='utf-8'))
#
#             results_list.append({host_obj.addr: str(result, encoding='utf-8')})
#
#         # 关闭连接
#         ssh.close()
#
#         return results_list
#
#
# if __name__ == '__main__':
#     FileTransfer()
