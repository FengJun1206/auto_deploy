from subprocess import PIPE, Popen


class BackDB:
    def migrations(self, src_host, src_user, src_pwd, src_db, desc_host, desc_user, desc_pwd, desc_db, desc_port=3306,
                   src_port=3306):
        """数据备份"""
        self.src_host, self.src_user, self.src_pwd, self.src_db, self.src_port = src_host, src_user, src_pwd, src_db, src_port
        self.desc_host, self.desc_user, self.desc_pwd, self.desc_port, self.desc_db = desc_host, desc_user, desc_pwd, desc_port, desc_db

        # 利用mysqldump命令备份
        dump = "mysqldump -h %s -P %s -u%s -p%s --default-character-set=utf8 --single-transaction --databases %s" % (
            self.src_host, self.src_port, self.src_user, self.src_pwd, self.src_db
        )

        # 利用mysql命令导入
        conn_cmd = 'mysql -u%s -p%s -P %s -h %s --default-character-set=utf8 %s' % (
        self.desc_user, self.desc_pwd, self.desc_port, self.desc_host, self.desc_db)
        # print(conn_cmd)

        # shell中的管道，管道用|符号分割两个命令，管道符前的命令正确输出作为管道符后命令的输入
        process = Popen("%s | %s" % (dump, conn_cmd), stderr=PIPE, shell=True)
        process_stdout = process.communicate()

        if process.returncode == 0:
            return True, None
        else:
            # print('备份失败')
            err_msg = process_stdout[1].decode('utf-8').strip()

            print('>>>>', err_msg)
            return False, err_msg


if __name__ == '__main__':
    BackDB().migrations('192.168.40.135', 'root', 'root', 'test', '192.168.188.110', 'root', 'root', 'test')
