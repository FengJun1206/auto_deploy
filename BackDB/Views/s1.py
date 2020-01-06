# import paramiko
#
#
# class Lazyconnection:
#     def __init__(self, addr, user, pwd, port=22):
#         self.addr = addr
#         self.user = user
#         self.pwd = pwd
#         self.port = port
#         self.connections = []
#
#     def __enter__(self):
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         ssh.connect(hostname=self.addr, username=self.user, password=self.pwd, port=self.port)
#         self.connections.append(ssh)
#
#         return ssh
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         print(self.connections)
#         print('连接断开', exc_type, exc_val, exc_tb)
#         self.connections.pop().close()
#
#
# host_list = [['192.168.40.135', 'dly', '1508', 22], ['192.168.188.145', 'vm145', '123456', 22]]
# for host in host_list:
#     conn = Lazyconnection(host[0], host[1], host[2], host[3])
#     with conn as s:
#         stdin, stdout, stderr = s.exec_command('ls')
#         result = stdout.read()
#         print(str(result, encoding='utf-8'))


# class A:
#     def spam(self):
#         print('A.spam')
#
#
# class B(A):
#     def spam(self):
#         print('B.spam')
#         super().spam()
#
#
# B().spam()


# class A:
#     def __init__(self):
#         self.x = 0
#
#
# class B(A):
#     def __init__(self):
#         super().__init__()
#         self.y = 1
#
# print(B().x, B().y)

