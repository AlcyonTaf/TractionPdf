# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
import os
import glob
import pandas as pd
import ghostscript
from tkinter import ttk, Text, OptionMenu, StringVar, filedialog as fd
from tkinter.messagebox import showinfo, showerror
from configparser import ConfigParser

# Recuperation de la configuration
config = ConfigParser()
config.read('config.ini')


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="red", *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.test_result_list = TestResultList(self)
        self.test_result_list.grid(row=0, column=1, sticky='news')
        self.details_text = Details(self)
        self.details_text.grid(row=1, column=1, sticky='news')

        # self.label = tk.Label(self, text="Test text")
        # self.label.grid(row=2, column=1)


class TestResultList(tk.Frame):
    """
    Class qui va generer l'affichage et la récupération des résultats des essais
    Pour cela on récupére la liste des dossier dans le dossier "Suivi"
    Un dossier est créer par jour, on utilise le nom du dossier pour afficher un drop down.
    Ce drop down permet de choisir les résultats qui seront dans le treeview
    """

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.frame = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_columnconfigure(0, weight=1)

        # define columns
        columns = ('um', 'commande', 'poste', 'lot', 'seqloc', 'seqessai', 'nbrepr')

        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        for i in range(len(columns) + 1):
            self.tree.column('#' + str(i), width=100, anchor='center', stretch=False)

        self.tree.heading('um', text='UM')
        self.tree.heading('commande', text='Commande')
        self.tree.heading('poste', text='Poste')
        self.tree.heading('lot', text='Lot')
        self.tree.heading('seqloc', text='Sequence Loc')
        self.tree.heading('seqessai', text='Sequence Essai')
        self.tree.heading('nbrepr', text='Nbr Epr')

        self.tree.grid(row=1, column=0, sticky='nesw')

        # Treeview event click => Pour affichage des info dans détails
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        # Treeview event click droit => pour affichage popup menu
        self.tree.bind("<Button-3>", self.show_popup_menu)

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=1, sticky='nse')
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Ajout d'un menu deroulant pour le choix de la date
        self.folderlist = StringVar()
        # TODO : Choix par defaut, voir pour choisir date du jour
        self.folderlist.set(self.get_result_date_list()[0])
        self.dropdown_export = OptionMenu(self, self.folderlist, *self.get_result_date_list(), command=self.get_df_csv)
        self.dropdown_export.grid(row=0, column=0)
        # callback du dropdown => pas utile au final car on utilise command=
        # self.folderlist.trace("w", self.callback_dropdown_export)

        #Création d'un menu popup lors du clic droit
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Envoyer annexe", command=self.popup_menu_send_pdf)
        self.popup_menu.add_command(label="Supprimer le fichier", command=self.popup_menu_delete_file)

    def popup_menu_send_pdf(self):
        """ Fonction pour l'envoie des PDF """
        # TODO : Voir si elle ne peut pas etre static
        file_path = fd.askopenfilename(title="Choix du PDF a transmettre a SAP", filetypes=[('PDF', '*.pdf')])
        print(file_path)
        csv_filepath = config.get('Annexe', 'SaveTiffFolder') + "\\test.tiff"
        print(csv_filepath)
        pdf_to_tiff(file_path, csv_filepath)

        pass

    def popup_menu_delete_file(self):
        print(self.popup_menu.selection)
        tk.messagebox.showinfo("Test", "test")

    def show_popup_menu(self, event):
        try:
            item = self.tree.identify_row(event.y)
            self.popup_menu.selection = self.tree.set(item)
            self.tree.focus(item)
            self.tree.selection_set(item)
            self.popup_menu.post(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def on_select(self, event):
        # Todo : Prévoir le cas ou la treeview est vide
        if len(self.tree.selection()) > 0:
            item = self.tree.selection()[0]
            idx = self.tree.index(item)
            #print(item)
            #print(idx)
            #print(self.tree.item(item, "value"))
            # On récupére tous les détails dans le df avec l'index
            #print(self.frame.iloc[[idx]])
            # On complete détails
            details_text = self.parent.details_text.text
            details_text.delete('1.0', 'end')
            # Todo : Voir pour afficher le nom du fichier correctement et non coupé
            details_text.insert('end', '\n' + str(self.frame.iloc[idx, 6:-1]))

    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            showinfo(title='Information', message=','.join(record))

    def get_result_date_list(self):
        # TODO : ne garder que la date
        os.chdir(config.get('ResultsFolder', 'SuiviPath'))
        result_list = ["En attente export"]
        result_list.extend([name for name in os.listdir(".") if os.path.isdir(name)])
        return result_list

    def callback_dropdown_export(self, *args):
        # TODO : Mettre a jour la treeview avec la liste des fichiers de résultats du dossier sélectionner

        # Essai modification partie détails
        details_text = self.parent.details_text.text
        print(self.parent.details_text.text.get('1.0', 'end'))
        details_text.insert('end', '\n' + 'sfsdfsfd')

    def get_df_csv(self, csv_folder_name):
        """ Fonction qui récupére les données des CSV et remplie la treeview"""
        if csv_folder_name == "En attente export":
            #print('test')
            csv_path = config.get('ResultsFolder', 'ExportFolder') + "\*.csv"
        else:
            root_path = config.get('ResultsFolder', 'SuiviPath')
            csv_path = root_path + "\\" + csv_folder_name + "\**\*.csv"

        # print(csv_path)
        self.frame = []
        li = []
        list_csv = [name for name in glob.glob(csv_path)]

        for filename in glob.glob(csv_path):

            # Vérification encodage
            with open(filename, 'rb') as f:
                first_four = f.read(4)
            if first_four[1] == 0 and first_four[3] == 0:
                encode = "utf_16_le"
            else:
                encode = "ascii"
            # création du dataframe
            df = pd.read_csv(filename, index_col=None, header=None, sep=';', encoding=encode,
                             names=["Commande", "Poste", "UM", "Sequence Essai", "Sequence Loc",
                                    "Nbr Epr", "Machine", "Date", "Opérateur", "Rp0.2", "ReH", "Rm", "ReL", "Rp0.5",
                                    "Rp1",
                                    "Rt0.5", "EYoung", "A Lo80mm", "A Lo50mm", "A Lo=2Inch", "A Lo200mm", "A Lo5.65VSo",
                                    "A Lo4d", "A Lo5d", "A Lo16mm", "Z%", "Z%Ind"])
            df['Nom fichier'] = filename
            # print(df)
            li.append(df)

        self.frame = pd.concat(li, axis=0, ignore_index=True)
        # Détection des doublons
        self.frame['double'] = self.frame.duplicated(keep=False,
                                                     subset=["Commande", "Poste", "UM", "Sequence Essai",
                                                             "Sequence Loc"])
        # print(type(frame))
        # On vide la treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Boucle sur la df et on remplie la treeview
        for n in range(len(self.frame.index.values)):
            # Récupération du N°UM avec position
            um = (os.path.basename(self.frame.iloc[n, -2]).split("-")[0],)
            # Récupération chemin
            filepath = self.frame.iloc[n, -2]
            # On concat le N°UM avec le reste des infos
            tout = um + tuple(self.frame.iloc[n, [0, 1, 2, 3, 4, 5]])

            # Essai pour mettre en couleur certain probleme
            # Si il n'y a pas d'UM dans le nom du fichier => envoie de résultat avec méthode sans QR
            if not um[0][:6].isdigit():
                row_color = "red"
            elif self.frame.iloc[n, -1]:
                row_color = "blue"
            elif filepath is not None and "error-csv" in filepath:
                row_color = "orange"
            else:
                row_color = ""

            self.tree.insert('', 'end', values=tout, tags=row_color)
            self.tree.tag_configure("red", background="red")
            self.tree.tag_configure("blue", background="blue")
            self.tree.tag_configure("orange", background="orange")


class Details(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="blue", *args, **kwargs)
        self.parent = parent

        self.configure(background='blue')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.label = tk.Label(self, text="Test text2")
        # self.label.pack()
        self.text = Text(self)
        self.text.grid(row=0, column=0, sticky='news')

        self.text.insert('1.0', 'ceci est un test')


class MenuTest(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        filemenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", underline=0, menu=filemenu)
        filemenu.add_command(label="Exit", underline=1, command=self.quit)


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        menubar = MenuTest(self)
        self.config(menu=menubar)

        self.title("Test")
        # self.geometry('640x480')
        # self.maxsize(800, 600)
        # self.minsize(300, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # MainApplication(self).pack(side="top", fill="both", expand=True)
        self.main_application = MainApplication(self)
        self.main_application.grid(row=0, column=0, sticky='nswe')
        # OtherFrame(self).pack(side="bottom")

    # afficher les erreurs
    # todo : a réactiver
    # def report_callback_exception(self, exc, val, tb):
    #     showerror("Error", message=str(val))


def pdf_to_tiff(path_to_pdf, path_export_tiff):
    # todo : mettre les parametres dans le config.ini
    args = [
        "ps2pdf",  # actual value doesn't matter
        "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-r150",
        "-sDEVICE=tiff24nc",
        "-sCompression=pack",
        "-sOutputFile=" + path_export_tiff,
        path_to_pdf
    ]
    try:
        ghostscript.Ghostscript(*args)
        return True
    except:
        return False



if __name__ == "__main__":
    app = App()
    # MainApplication(root).pack(side="top", fill="both", expand=True)
    app.mainloop()
