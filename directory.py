import os
from configparser import ConfigParser

config = ConfigParser()

config.read('config.ini')
# path = os.getcwd()
# print(path+'\Suivi')
# os.chdir(config.get('ResultsFolder', 'SuiviPath'))
# print([name for name in os.listdir(".") if os.path.isdir(name)])


def get_result_date_list():
    os.chdir(config.get('ResultsFolder', 'SuiviPath'))
    list = [name for name in os.listdir(".") if os.path.isdir(name)]

    return list

