from datetime import datetime

from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash

from utils.common.LogHandle import log

logger = log(__name__)

db = SQLAlchemy()


class UserProfile(db.Model):
    """用户表"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(128))
    is_super = db.Column(db.Boolean, default=0)
    created_time = db.Column(db.DateTime, default=datetime.now())

    task = db.relationship('Task', backref='userprofile', lazy='dynamic')

    def __repr__(self):
        return '%s' % self.username

    def set_password(self, password):
        """密码加密"""

        return generate_password_hash(password)

    def check_password(self, username, password):
        """检查密码是否加密"""
        origin_pwd = UserProfile.query.filter_by(username=username)[0].password

        return check_password_hash(origin_pwd, password)

    def change_password(self, password):
        """修改密码"""
        self.password = self.set_password(password)

    @classmethod
    def check_user(cls, username):
        """检查用户名是否被注册"""
        user = cls.query.filter_by(username=username).all()
        if not user:
            return False
        return True


class Host(db.Model):
    """主机表"""
    __tablename__ = 'host'
    id = db.Column(db.Integer, primary_key=True)
    addr = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(32))
    password = db.Column(db.String(64))
    port = db.Column(db.Integer, default=22)

    database = db.relationship('DB', backref='host', lazy='dynamic')  # 一对多之一

    def __repr__(self):
        return '%s-%s' % (self.addr, self.port)

    @classmethod
    def queryset(cls):
        """获取数据库列表"""
        return cls.query.all()

    @classmethod
    def filter(cls, host):
        """获取数据"""
        return cls.query.filter_by(addr=host).all()

    @classmethod
    def test_connect(cls, host, user, pwd, port):
        """测试连接，检查是否错误"""
        ret = {'code': 0, 'msg': 'success', 'data': None}

        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=host, username=user, password=pwd, port=port)
        except Exception as e:
            ret['code'] = e.args[0]
            ret['msg'] = 'failed'
            ret['data'] = e.args[1]
            logger.error('测试远程主机连接发生错误：%s，原因：%s' % (host, e.args))
        finally:
            ssh.close()

        return ret


class DB(db.Model):
    """数据库"""
    __tablename__ = 'db'

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(32))
    password = db.Column(db.String(64))
    port = db.Column(db.Integer, default=3306)
    db_name = db.Column(db.String(32))

    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))  # 一对多之多

    def __repr__(self):
        return '%s-%s' % (self.user, self.db_name)

    @classmethod
    def queryset(cls):
        """获取数据库列表"""
        return cls.query.all()

    @classmethod
    def filter(cls, db_name):
        """获取数据"""
        return cls.query.filter_by(db_name=db_name).all()

    @classmethod
    def test_connect(cls, host, user, pwd, port, db_name):
        """测试数据库连接"""
        ret = {'code': 0, 'msg': 'success', 'data': None}
        import pymysql

        try:
            conn = pymysql.connect(host=host, user=user, password=pwd, port=int(port),
                                   database=db_name)
            cursor = conn.cursor()
            sql = """show tables;"""
            # 执行SQL语句
            cursor.execute(sql)
            # 关闭光标对象
            cursor.close()
            conn.close()  # 关闭数据库连接
            ret['msg'] = 'success'
        except Exception as e:
            logger.error('测试数据库连接发生错误：%s，原因：%s' % (host, e.args))
            ret['code'] = e.args[0]
            ret['msg'] = 'failed'
            ret['data'] = e.args[1]

        return ret


class Task(db.Model):
    """任务表"""
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    task_type_choices = {
        0: 'fle',
        1: 'cmd',
    }
    task_type = db.Column(db.Integer, default=task_type_choices[0])
    command = db.Column(db.String(128), nullable=False)  # 命令
    remote_host = db.Column(db.String(32))  # 操作的远程主机
    result = db.Column(db.Text())  # 命令执行结果
    created_time = db.Column(db.DateTime, default=datetime.now())  # 创建时间

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return self.task_type

    @classmethod
    def save_result(cls, command, result_list):
        """
        存入命令执行结果
        :param command: 命令
        :param result_list: 任务结果，[{'主机1': 'xxx'}, {'主机2', 'xxxx'}]
        :return:
        """
        try:
            name = session.get('username')
            user_id = UserProfile.query.filter_by(username=name)[0].id
            for i in result_list:
                task = cls(task_type=0, command=command, remote_host=list(i.keys())[0], result=list(i.values())[0],
                           user_id=user_id)
                db.session.add(task)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error('插入批量任务结果发生错误：%s' % e.args)

