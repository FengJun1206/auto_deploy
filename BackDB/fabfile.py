import os
import zipfile

from fabric.api import *


env.hosts = ['192.168.40.135']
env.user = 'dly'
env.password = '1508'

remote_dir = '/home/dly/auto_deploy/'


@runs_once
def local_update():
    """上传本地代码到 github"""

    pass


@task
def remote_update():
    """远程服务器从 git 上拉取最新代码"""
    run('mkdir -p %s' % remote_dir)
    with cd(remote_dir):
        # 从 git 上拉取代码
        pass


@task
def run_task():
    """创建 Python 虚拟环境，安装 docker-compose，docker 启动项目"""
    # 切换到工作目录
    with cd(remote_dir):
        run('mkvirtualenv -p python3 auto_deploy')
        run('workon auto_deploy')
        run('pip install docker-compose -i https://pypi.douban.com/simple')
        run('docker-compose build')
        run('docker-compose up -d')
        run('supervisorctl start wssh')

@task
def go():
    local_update()
    remote_update()
    run_task()





