from flask_wtf import FlaskForm
# 导入自定义表单需要的字段
from wtforms import SubmitField, StringField, PasswordField
# 导入wtf扩展提供的表单验证器
from wtforms.validators import DataRequired, EqualTo, Required, Length, InputRequired


class RemoteForm(FlaskForm):
    """远程主机"""
    src_host = StringField(label='原主机名', validators=[DataRequired(), Length(1, 15, message=u'长度不超过15个字符')])
    src_port = StringField(label='端口', validators=[DataRequired(), Length(1, 6, message=u'长度不超过6个字符')])
    src_user = StringField(label='用户名', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    src_pwd = PasswordField(label='密码', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    src_db = StringField(label='数据库', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    desc_host = StringField(label='目标主机名', validators=[DataRequired(), Length(1, 15, message=u'长度不超过15个字符')])
    desc_port = StringField(label='端口', validators=[DataRequired(), Length(1, 6, message=u'长度不超过6个字符')])
    desc_user = StringField(label='用户名', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    desc_pwd = PasswordField(label='密码', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    desc_db = StringField(label='数据库', validators=[DataRequired(), Length(1, 20, message=u'长度不超过20个字符')])
    src_submit = SubmitField('提交')


class RegisterForm(FlaskForm):
    name = StringField(label='用户名', validators=[DataRequired(u'用户名不能为空'), Length(1, 15, message=u'长度 1-15 字符')])
    password = PasswordField(label='密码', validators=[DataRequired(u'密码不能为空'), Length(6, 9, message=u'密码长度是6到9')])
    re_password = PasswordField(label='确认密码', validators=[DataRequired(u'密码不能为空'), EqualTo('password', message=u'两次密码不一致')])


class LoginForm(FlaskForm):
    name = StringField(label='用户名', validators=[DataRequired(u'用户名不能为空'), Length(1, 15, message=u'长度 1-15 字符')])
    password = PasswordField(label='密码', validators=[DataRequired(u'密码不能为空'), Length(6, 9, message=u'密码长度是6到9')])


class HostForm(FlaskForm):
    """主机"""
    host = StringField(label='主机名', validators=[DataRequired(u'主机名不能为空'), Length(1, 15, message=u'长度 1-15 字符')])
    user = StringField(label='用户名', validators=[DataRequired(u'用户名不能为空'), Length(1, 15, message=u'长度 1-15 字符')])
    password = PasswordField(label='密码', validators=[DataRequired(u'密码不能为空'), Length(1, 20, message=u'密码长度是1到20')])
    port = StringField(label='端口', validators=[DataRequired(u'端口不能为空'), Length(1, 6, message=u'长度 1-6 字符')])


class DBForm(FlaskForm):
    """数据库"""
    user = StringField(label='用户名', validators=[DataRequired(u'用户名不能为空'), Length(1, 15, message=u'长度 1-15 字符')])
    password = PasswordField(label='密码', validators=[DataRequired(u'密码不能为空'), Length(4, 32, message=u'密码长度是4到32')])
    port = StringField(label='端口', validators=[DataRequired(u'端口不能为空'), Length(1, 6, message=u'长度 1-6 字符')])
    db = StringField(label='数据库', validators=[DataRequired(u'数据库不能为空'), Length(1, 10, message=u'长度 1-10 字符')])
