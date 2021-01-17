import os
import configparser

#os.path.realpath：获取当前执行脚本的绝对路径。
#os.path.split：如果给出的是一个目录和文件名，则输出路径和文件名
proDir = os.path.split(os.path.realpath(__file__))[0]
#configUrl = "../conf/config.ini"
configUrl = os.getenv('HOME')+"/conf/config.ini"
configPath = os.path.join(proDir, configUrl)


class ReadConfig:
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(configPath)

    def get_okex(self, param):
        value = self.cf.get("OKEX", param)
        return value

    def _get_okex(self, param):
        value = self.cf.get("OKEX", param)
        return value

    def get_db(self, param):
        value = self.cf.get("DATABASE", param)
        return value
    def get_env(self):
        value = os.getenv('HOME')
        return value

    def get_dbURL(self):
        return 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            self.cf.get("DATABASE", 'username'),
            self.cf.get("DATABASE", 'password'),
            self.cf.get("DATABASE", 'host'),
            self.cf.get("DATABASE", 'port'),
            self.cf.get("DATABASE", 'database'))


if __name__ == '__main__':

    test = ReadConfig()
    LocalIp = test.get_dbURL()
    print(LocalIp)
    print(test.get_env())