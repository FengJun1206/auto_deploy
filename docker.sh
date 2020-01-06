#! /bin/bash

# 检查是否 root 身份启动
function checkSudo() {
	if [ $UID -ne 0 ]
	then
		echo -e "It must be root!"
		echo -e "Usage sudo ./docker.sh {run|restart|drun|logs|stop}"
		exit 1
	fi
}

checkSudo

# 启用 Python 虚拟环境
source /root/.virtualenvs/auto_deploy/bin/activate
# pip install docker-compose -i https://pypi.douban.com/simple

# 根据输入参数调用相应命令，操作 docker 容器
if [ $# -eq 1 ]
then
	case $1 in
		"run")
			docker-compose up
			supervisorctl start wssh;;
		"restart")
			docker-compose restart
			supervisorctl restart wssh;;
		"drun")			
			docker-compose up -d;;
		"logs")
			docker-compose logs;;
		"stop")
			docker-compose down
			supervisorctl stop wssh;;
		*)
			echo -e "Usage sudo ./docker.sh {run|restart|drun|logs|stop}"
	esac
else
	echo -e "Usage sudo ./docker.sh {run|restart|drun|logs|stop}"
fi

