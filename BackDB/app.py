import functools
import threading
from datetime import timedelta

from flask import Flask, redirect, url_for, render_template, request, flash, views, \
    copy_current_request_context, session
import json
import uuid
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sse import sse

from Views.forms import RemoteForm, RegisterForm, LoginForm, HostForm, DBForm
from utils.common.back_db import BackDB
from utils.common.conn_server import do_run_command
from utils.common.file_transfer import BatchOperation
from models import UserProfile, Host, DB, Task
from admin import UserAdmin
from utils.common.LogHandle import log
from utils.common.security import encrypt_oracle

logger = log(__name__)

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_pyfile('config.py')
app.register_blueprint(sse, url_prefix='/stream')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@192.168.188.145:3308/Flask_test'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 设置每次请求结束后会自动提交数据库中的改动
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.nginx['SQLALCHEMY_ECHO'] = True    # 查询时会显示原始SQL语句
db = SQLAlchemy(app)

# flask admin 主题
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(UserAdmin(db.session, name='用户表'))
admin.add_view(ModelView(Host, db.session))
admin.add_view(ModelView(DB, db.session))


def check_login(func):
    """验证登陆装饰器"""

    @functools.wraps(func)  # 修改内存函数，防止当前装饰器取修改被装饰函数属性
    def wrapper(*args, **kwargs):
        name = session.get('username')
        if not name:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper


class IndexHandle(views.MethodView):
    """首页"""

    @check_login
    def get(self):
        host_list = Host.queryset()
        form = DBForm()

        return render_template('index.html', host_list=host_list, form=form)


class DbHandle(views.MethodView):
    """数据库处理"""

    @check_login
    def get(self, host):
        form = DBForm()
        return render_template('db.html', form=form, host=host)

    def post(self, host):
        form = DBForm(request.form)

        if form.validate_on_submit():
            user, db_name = request.form['user'], request.form['db']
            pwd, port = request.form['password'], request.form['port']

            # 检查数据库是否存在
            if DB.filter(db_name):
                flash('数据库已存在！')
            else:
                # 验证测试
                result = DB.test_connect(host, user, pwd, port, db_name)
                if result['code'] != 0:
                    flash('连接失败，请检查相关配置！')

                # 存入数据库
                host_id = Host.filter(host)[0].id
                db_obj = DB(user=user, password=encrypt_oracle(pwd), port=port, db_name=db_name, host_id=host_id)
                db.session.add(db_obj)
                db.session.commit()
                return redirect(url_for('index'))

        return render_template('db.html', form=form, host=host)


@app.route('/back', methods=['POST', 'GET'])
@check_login
def back():
    """数据迁移备份"""
    form = RemoteForm()

    if request.method == 'POST':
        try:
            if form.validate_on_submit():
                # 原主机信息
                src_host = form.src_host.data
                src_user = form.src_user.data
                src_pwd = form.src_pwd.data
                src_port = form.src_port.data
                src_db = form.src_db.data

                # 目标主机信息
                desc_host = form.desc_host.data
                desc_user = form.desc_user.data
                desc_pwd = form.desc_pwd.data
                desc_port = form.desc_port.data
                desc_db = form.desc_db.data

                # print(src_host, src_user, src_pwd, src_port, src_db, desc_db, desc_host, desc_port, desc_pwd,desc_user)
                status, result = BackDB().migrations(src_host, src_user, src_pwd, src_db, desc_host, desc_user,
                                                     desc_pwd,
                                                     desc_db,
                                                     desc_port, src_port)
                if status:
                    flash('迁移成功！')
                    logger.info('数据库迁移备份成功：%s ==> %s' % (src_host, desc_host))
                    return redirect(url_for('index'))
                else:
                    flash('迁移失败！\n %s' % result)
                    return render_template('back.html', form=form)
        except Exception as e:
            logger.error('数据库迁移备份发生错误：%s' % e)
    else:
        return render_template('back.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册"""
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form=form)
    else:
        if form.validate_on_submit():
            username = request.form['name']
            password = UserProfile().set_password(request.form['password'])
            # 检查用户名是否被注册
            if UserProfile.check_user(request.form['name']):
                flash('该用户已被注册！')
                return render_template('register.html', form=form)
            print(username, password, len(password))

            user = UserProfile(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('注册成功！')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登陆"""
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username, password = request.form['name'], request.form['password']
            if not UserProfile.check_user(username):
                flash('用户名不存在！')
                return render_template('login.html', form=form)

            # 检查密码是否正确
            if not UserProfile().check_password(username, password):
                flash('密码不正确！')
                return render_template('login.html', form=form)

            # 存入 session
            session['username'] = form.name.data
            app.permanent_session_lifetime = timedelta(hours=2)  # 设置session到期时间
            return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """登出"""
    # 从 session 移除 username
    session.pop('username', None)
    return redirect(url_for('login'))


class LogHandle(views.MethodView):
    @check_login
    def get(self):
        """监控日志"""
        host_list = Host.queryset()

        return render_template('tail.html', host_list=host_list)

    def post(self):
        host = request.form.get('host')
        command = request.form.get('command')
        uid = uuid.uuid4().hex
        th = threading.Thread(target=copy_current_request_context(do_run_command), args=(host, command, uid))
        th.start()

        return {'uid': uid}


class FileHandle(views.MethodView):
    """文件上传下载"""

    @check_login
    def get(self):
        host_list = Host.queryset()

        return render_template('file.html', host_list=host_list)

    def post(self):
        local_file_path = request.form.get('local').strip()
        local_file_path = local_file_path.replace('\\', '/')  # Windows 文件路径转换
        remote_file_path = request.form.get('remote').strip()
        url = request.url.split('?flag=')[1]
        host_list = json.loads(request.form.get('host_list'))  # 主机列表
        host_list = [i.split('@')[1] for i in host_list]

        try:
            if url == "upload":  # 上传
                BatchOperation().send(local_file_path, remote_file_path, host_list)
                logger.info('文件上传成功！')
            else:
                BatchOperation().get(local_file_path, remote_file_path, host_list)
                logger.info('文件下载成功！')
            ret = {'code': 0, 'msg': '传输成功！'}
        except Exception as e:
            print('上传下载文件失败，原因：', e.args)
            ret = {'code': 102, 'msg': e.args}
            logger.error('上传下载文件失败，原因：%s' % e.args)

        return json.dumps(ret)


class BatchCmd(views.MethodView):
    """批量命令"""

    @check_login
    def get(self):
        host_list = Host.queryset()

        return render_template('cmd.html', host_list=host_list)

    def post(self):
        host_list = json.loads(request.form.get('host_list'))  # 主机列表
        host_list = [i.split('@')[1] for i in host_list]
        cmd = request.form.get('cmd').strip()

        print(host_list, cmd)

        try:
            result_list = BatchOperation().exec_cmd(host_list, cmd)
            # 将命令执行结果写入数据库
            Task.save_result(cmd, result_list)

            logger.info('批量命令执行成功！')
            ret = {'code': 0, 'msg': '执行成功！', 'data': result_list}
        except Exception as e:
            logger.error('批量命令执行失败，原因：%s' % e.args)
            ret = {'code': 0, 'msg': '执行失败！'}

        return json.dumps(ret)


class Order(views.MethodView):
    """工单处理"""

    @check_login
    def get(self):
        form = HostForm()

        return render_template('order.html', form=form)

    def post(self):
        form = HostForm(request.form)
        if form.validate_on_submit():
            host, user = request.form['host'], request.form['user']
            pwd, port = request.form['password'], request.form['port']
            # 检查主机是否已存在
            if Host.filter(host):
                flash('主机已存在！')
            else:
                # 测试密码是否正确，是否能连接成功
                result = Host.test_connect(host, user, pwd, port)
                if result['code'] == 0:
                    password = encrypt_oracle(pwd)
                    host_obj = Host(addr=host, name=user, password=password, port=port)
                    db.session.add(host_obj)
                    db.session.commit()

                    return redirect(url_for('index'))
                else:
                    flash('添加失败，请检查参数是否正确！')

        return render_template('order.html', form=form)


app.add_url_rule('/', view_func=IndexHandle.as_view(name='index'))
app.add_url_rule('/file', view_func=FileHandle.as_view(name='file'))
app.add_url_rule('/cmd', view_func=BatchCmd.as_view(name='cmd'))
app.add_url_rule('/tail', view_func=LogHandle.as_view(name='tail'))
app.add_url_rule('/order', view_func=Order.as_view(name='order'))
app.add_url_rule('/db/<host>', view_func=DbHandle.as_view(name='db'))


if __name__ == '__main__':
    app.run()
