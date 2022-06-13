import os
from configparser import ConfigParser
from datetime import datetime

config = ConfigParser()
config.read('config.ini')
os.chdir(config.get('ResultsFolder', 'SuiviPath'))
result_list = ["En attente export"]

List_folder = [name for name in os.listdir(".") if os.path.isdir(name)]
result_list.extend([name for name in os.listdir(".") if os.path.isdir(name)])

List_folder.sort(key=lambda x: datetime.strptime(x.split(' ')[2], "%d-%m-%y"), reverse=True)

def get_date():
    date = []
    for folder in List_folder:
        date.append(folder.split(' ')[2])
        test = datetime.strptime(folder.split(' ')[2], "%d-%m-%y")
        # print(test)
        # print(type(test))

    #print(date)
    date.sort(key=lambda x: datetime.strptime(x, "%d-%m-%y"), reverse=True)
    print(date)


print(List_folder)
# print(type(List_folder))


