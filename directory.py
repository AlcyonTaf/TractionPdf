import os
path = os.getcwd()
print(path+'\Suivi')
os.chdir(path+'\Suivi')
print ([name for name in os.listdir(".") if os.path.isdir(name)])