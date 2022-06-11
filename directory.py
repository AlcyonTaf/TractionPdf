import os
import glob
import pandas as pd
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


def get_list_csv():
    list = [name for name in glob.glob(
        'E:\Romain\Documents\Romain bidouille\Informatique\Taf\TractionPdf\Suivi\Export du 27-05-22\CSV\*.csv')]
    return list


# print(get_list_csv()[0])

li = []


for filename in get_list_csv():
    # Vérification encodage
    with open(filename, 'rb') as f:
        first_four = f.read(4)
    if first_four[1] == 0 and first_four[3] == 0:
        encode = "utf_16_le"
    else:
        encode = "ascii"

    #print(filename)
    #os.path.basename(filename)[:6].isdigit()

    #print(os.path.basename(filename)[:6])
    #print(os.path.basename(filename))
    df = pd.read_csv(filename, index_col=None, header=None, sep=';', encoding=encode,
                     names=["Commande", "Poste", "UM", "Sequence Essai", "Sequence Loc",
                            "Nbr Epr", "Machine", "Date", "Opérateur", "Rp0.2", "ReH", "Rm", "ReL", "Rp0.5", "Rp1",
                            "Rt0.5", "EYoung", "A Lo80mm", "A Lo50mm", "A Lo=2Inch", "A Lo200mm", "A Lo5.65VSo",
                            "A Lo4d", "A Lo5d", "A Lo16mm", "Z%", "Z%Ind"])
    df['Nom fichier'] = filename
    # print(df)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)

frame['double'] = frame.duplicated(keep=False, subset=["Commande", "Poste", "UM", "Sequence Essai", "Sequence Loc"])


for n in range(len(frame.index.values)):
    print("ok")
    # um = (os.path.basename(frame.iloc[n, -1]).split("-")[0],)
    #other = um + tuple(frame.iloc[n, [0, 1, 2, 3 , 4, 5]])


    #print(frame.iloc[n, -1])
    #print((frame.iloc[n, [2, 0, 1]]))


