# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from tkinter import ttk, Text, OptionMenu, StringVar
from tkinter.messagebox import showinfo
import os
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

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=10)
        self.grid_columnconfigure(0, weight=1)

        # define columns
        columns = ('um', 'commande', 'poste')

        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        self.tree.heading('um', text='UM')
        self.tree.heading('commande', text='Commande')
        self.tree.heading('poste', text='Poste')

        # generate sample data
        # contacts = []
        # for n in range(1, 100):
        #     contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))
        #
        # # add data to the treeview
        # for contact in contacts:
        #     self.tree.insert('', tk.END, values=contact)
        # self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=1, column=0, sticky='nesw')

        # add a scrollbar
        # scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        # tree.configure(yscroll=scrollbar.set)
        # scrollbar.grid(row=0, column=1, sticky='ns')

        # Ajout d'un menu deroulant pour le choix de la date
        self.folderlist = StringVar()
        # TODO : Choix par defaut, voir pour choisir date du jour
        self.folderlist.set(self.get_result_date_list()[0])
        self.dropdown_export = OptionMenu(self, self.folderlist, *self.get_result_date_list())
        self.dropdown_export.grid(row=0, column=0)
        # callback du dropdown
        self.folderlist.trace("w", self.callback_dropdown_export)

    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            showinfo(title='Information', message=','.join(record))

    def get_result_date_list(self):
        # TODO : ne garder que la date
        os.chdir(config.get('ResultsFolder', 'SuiviPath'))
        resultlist = [name for name in os.listdir(".") if os.path.isdir(name)]
        return resultlist

    def callback_dropdown_export(self, *args):
        # TODO : Mettre a jour la treeview avec la liste des fichiers de résultats du dossier sélectionner
        details_text = self.parent.details_text.text
        print(self.parent.details_text.text.get('1.0', 'end'))
        details_text.insert('end', '\n' + 'sfsdfsfd')


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
        self.geometry('640x480')
        self.maxsize(800, 600)
        self.minsize(300, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # MainApplication(self).pack(side="top", fill="both", expand=True)
        MainApplication(self).grid(row=0, column=0, sticky='nswe')
        # OtherFrame(self).pack(side="bottom")


def hello():
    print("hello!")


if __name__ == "__main__":
    app = App()
    # MainApplication(root).pack(side="top", fill="both", expand=True)
    app.mainloop()
