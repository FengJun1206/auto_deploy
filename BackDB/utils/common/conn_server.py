import paramiko
import select
from flask_sse import sse

from models import Host
from utils.common.security import decrypt_oralce
from utils.common.LogHandle import log

logger = log(__name__)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)     # 允许连接不在know_hosts文件中的主机


def do_run_command(host, command, uid):
    try:
        host_obj = Host.filter(host)[0]
        password = decrypt_oralce(host_obj.password)  # 解密

        # print(host_obj.addr, host_obj.port, host_obj.name, password)
        ssh.connect(hostname=host_obj.addr, port=host_obj.port, username=host_obj.name, password=password)    # 连接服务器
        stdin, stdout, stderr = ssh.exec_command(command)

        channel = stdout.channel
        pending = err_pending = None

        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            readq, _, _ = select.select([channel], [], [], 1)
            for c in readq:
                # 有标准输出
                if c.recv_ready():
                    chunk = c.recv(len(c.in_buffer))
                    if pending is not None:
                        chunk = pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        pending = lines.pop()
                    else:
                        pending = None

                    [push_log(line.decode(), uid) for line in lines]

                # 有标准错误输出
                if c.recv_stderr_ready():
                    chunk = c.recv_stderr(len(c.in_stderr_buffer))
                    if err_pending is not None:
                        chunk = err_pending + chunk
                    lines = chunk.splitlines()
                    if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                        err_pending = lines.pop()
                    else:
                        err_pending = None

                    [push_log(line.decode(), uid) for line in lines]

    except Exception as e:
        logger.error("远程连接发生错误：%s" % e)
        print("远程连接发生错误：%s" % e)
    finally:
        logger.info("远程连接关闭：%s" % ssh)
        ssh.close()


def push_log(message, channel):
    sse.publish({'message': message}, 'message', channel=channel)


