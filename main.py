# Interface graphique
import tkinter as tk
# Utilitaire fichier/dossier
import os
# Trouver tous les fichiers d'un dossier
import glob
# Manipulation de données
import pandas as pd
# Pour générer un Tiff à partir d'un PDF
import ghostscript
# Pour copier/déplacer fichier
import shutil
from datetime import datetime
# Manipulation de xml
from lxml import etree as et
from tkinter import ttk, Text, OptionMenu, StringVar, filedialog as fd
from tkinter.messagebox import showinfo, showerror
# Gestion d'un fichier de configuration
from configparser import ConfigParser


# todo : rajouter description du programme et explication

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
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

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

        self.tree.grid(row=1, column=0, columnspan=3, sticky='nesw')

        # Treeview event click => Pour affichage des info dans détails
        self.tree.bind("<<TreeviewSelect>>", self.on_select_treeview_item)
        # Treeview event click droit => pour affichage popup menu
        self.tree.bind("<Button-3>", self.show_popup_menu)

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=3, sticky='nse')
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Ajout d'un menu déroulant pour le choix de la date
        self.result_date_list = get_result_date_list()
        self.folder_list = StringVar()
        self.folder_list.set(self.result_date_list[0])
        self.dropdown_export = OptionMenu(self, self.folder_list, *self.result_date_list, command=self.get_df_csv)
        self.dropdown_export.grid(row=0, column=0)
        # callback du dropdown => pas utile au final car on utilise command=
        # self.folderlist.trace("w", self.callback_dropdown_export)

        # Ajout d'une entrée pour recherche par UM
        self.search_entry = tk.Entry(self, width=15)
        self.search_entry.grid(row=0, column=1, sticky="e", padx=2)
        self.btn_search = tk.Button(self, text="rechercher", width=10, command=self.search_tree_view)
        self.btn_search.grid(row=0, column=2, sticky="w", padx=2)

        # Création d'un menu popup lors du clic droit
        self.popup_menu = tk.Menu(self, tearoff=0)

    def search_tree_view(self):
        """ Fonction pour rechercher dans la treeview par sélection """
        children = self.tree.get_children()
        search_value = self.search_entry.get()
        search_result = []
        for child in children:
            um_value = self.tree.item(child, 'value')[0]
            if um_value.lower().startswith(search_value.lower()):
                # print(search_value)
                # print("trouvé")
                # print(um_value)
                search_result.append(child)

        if search_result:
            self.tree.selection_set(search_result)
        else:
            if self.tree.selection():
                self.tree.selection_remove(self.tree.selection())

    def popup_menu_send_pdf(self):
        """ Fonction pour l'envoie des PDF """
        result_sap = []
        file_path = fd.askopenfilename(title="Choix du PDF a transmettre a SAP", filetypes=[('PDF', '*.pdf')])
        if file_path and len(self.tree.selection()) == 1:
            item = self.tree.selection()[0]
            essais_id = self.tree.item(item, "value")
            try:
                # On converti le PDF en TIFF, qui nous retourne le nom du pdf
                pdf_name = pdf_to_tiff(file_path, essais_id)
                # on créer le XML
                xml_pdf_to_tiff(essais_id, pdf_name)
            except Exception as value:
                showerror("Erreur Annexe!", "Une erreur c'est produit lors de la génération : " + str(value))
            else:
                # on va copier, en faisant attention au droit les fichiers généré dans le dossier d'échange avec SAP
                # Puis on archive les originaux en les déplaçant en ajoutant la date dans le nom du dossier
                src_folder = config.get('Annexe', 'SaveXMLTiffFolder')
                dst_folder = config.get('SAP', 'AICFolder')
                dst_archive_folder = config.get('Annexe', 'ArchiveFolderXmlTiff')
                files = [name for name in glob.glob(src_folder + "/*")]
                print(files)
                for file in files:
                    if os.path.isfile(file):
                        filename = os.path.basename(file)
                        dst = os.path.join(dst_folder, filename)
                        # Todo : Penser a vérifier que les droits sont correct sur destination
                        try:
                            result = shutil.copyfile(file, dst)
                        except Exception as e:
                            showerror("Erreur Annexe!", "Une erreur c'est produit lors de la copie dans le dossier "
                                                        "SAP : " + str(e))
                        else:
                            result_sap.append(os.path.basename(result))
                            # si pas d'erreur on archive
                            dst = os.path.join(dst_archive_folder, filename)
                            result_archive = shutil.move(file, dst)
                            print(result_archive)
        if result_sap:
            showinfo("Annexe transmise", " Liste des fichiers transmis :\n" + "\n".join(map(str, result_sap)))

    def delete_file(self):
        if len(self.tree.selection()) == 1:
            item = self.tree.selection()[0]
            idx = self.tree.index(item)
            file = str(self.frame.iloc[idx, -2])
            print(str(self.frame.iloc[idx, -2]))
            if os.path.exists(file):
                os.remove(file)
                self.get_df_csv('En attente export')

    def show_popup_menu(self, event):
        # Todo : voir pour ne pas afficher annexe si essai faux (red)
        item = self.tree.identify_row(event.y)
        if item:
            try:
                self.popup_menu.selection = self.tree.set(item)
                self.tree.focus(item)
                self.tree.selection_set(item)
                self.popup_menu.post(event.x_root, event.y_root)
            finally:
                self.popup_menu.grab_release()

    def on_select_treeview_item(self, event):
        if len(self.tree.selection()) > 0:
            item = self.tree.selection()[0]
            idx = self.tree.index(item)
            # print(item)
            # print(idx)
            # print(self.tree.item(item, "value"))
            # On récupére tous les détails dans le df avec l'index
            # print(self.frame.iloc[[idx]])
            # On complete détails
            details_text = self.parent.details_text.text
            details_text.config(state='normal')
            details_text.delete('1.0', 'end')
            # Todo : Voir pour afficher le nom du fichier correctement et non coupé
            details_text.insert('end', '\n' + str(self.frame.iloc[idx, 6:-1]))
            details_text.config(state='disabled')

    # def item_selected(self, event):
    #     for selected_item in self.tree.selection():
    #         item = self.tree.item(selected_item)
    #         record = item['values']
    #         # show a message
    #         showinfo(title='Information', message=','.join(record))

    # def callback_dropdown_export(self, *args):
    #     # Essai modification partie détails
    #     details_text = self.parent.details_text.text
    #     print(self.parent.details_text.text.get('1.0', 'end'))
    #     details_text.insert('end', '\n' + 'sfsdfsfd')

    def get_df_csv(self, csv_folder_name):
        """ Fonction qui récupére les données des CSV et remplie la treeview
            On en profite également pour completer le menu popup"""

        # Définition du menu popup a chaque fois qu'on sélectionne un item de la liste
        self.popup_menu.delete(0, 'end')
        self.popup_menu.add_command(label="Envoyer annexe", command=self.popup_menu_send_pdf)

        if csv_folder_name == "En attente export":
            # print('test')
            csv_path = config.get('ResultsFolder', 'ExportFolder') + "\*.csv"
            self.popup_menu.add_command(label="Supprimer le fichier", command=self.delete_file)
        else:
            root_path = config.get('ResultsFolder', 'SuiviPath')
            csv_path = root_path + "\\" + csv_folder_name + "\**\*.csv"

        # print(csv_path)
        self.frame = []
        li = []
        list_csv = [name for name in glob.glob(csv_path)]
        # Vérification si le dossier contient des fichiers
        if list_csv:
            # Todo rajouter vérification si fichier
            for filename in list_csv:
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
                                        "Rt0.5", "EYoung", "A Lo80mm", "A Lo50mm", "A Lo=2Inch", "A Lo200mm",
                                        "A Lo5.65VSo",
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
        else:
            # On vide la treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            showinfo("Pas de fichier!", "Aucun fichier n'est présent dans le dossier")


class Details(tk.Frame):
    """ Class pour afficher les détails d'un essai"""

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


class ArchivePopup(tk.Toplevel):
    """ Class pour afficher une fenêtre afin de faire l'archivage des dossiers d'export"""

    def __init__(self):
        tk.Toplevel.__init__(self)

        self.geometry('150x300')
        self.title('Archivage')
        # self.frame = tk.Frame(self)
        # self.frame.rowconfigure(0, weight=1)
        # self.frame.columnconfigure(0, weight=1)
        # self.frame.grid(row=0, column=0, sticky='nesw')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Ajout d'une listbox
        self.listbox = tk.Listbox(self, selectmode='multiple', activestyle='none', exportselection=0)
        self.suivi_folder = get_result_date_list()
        self.suivi_folder.remove("En attente export")
        for folder in self.suivi_folder:
            self.listbox.insert('end', folder)

        self.listbox.grid(row=0, column=0, sticky='wsne')

        # Ajout de la scrollbar
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        # Ajour du bouton archivé
        self.btn_archive = tk.Button(self, text="Archiver", command=self.archive_suivi)
        self.btn_archive.grid(row=1, column=0, sticky='s')

    def archive_suivi(self):
        result_archive = []
        if len(self.listbox.curselection()) > 0:
            for i in self.listbox.curselection():
                src = config.get('ResultsFolder', 'SuiviPath')
                dst = config.get('ResultsFolder', 'ArchiveSuivi')
                src_path = os.path.join(src, self.listbox.get(i))
                print(src_path)
                if os.path.isdir(src_path):
                    try:
                        result = shutil.move(src_path, dst)
                    except Exception as e:
                        # Todo : voir pour afficher un message d'erreur a la fin
                        showerror("Erreur Archivage!", "Une erreur c'est produit lors de l'archivage"
                                                       "SAP : " + str(e))
                    else:
                        result_archive.append(os.path.basename(os.path.normpath(result)))

            if result_archive:
                showinfo("Archivage Terminé", " Liste des dossiers archivés :\n" + "\n".join(map(str, result_archive)))
        else:
            showinfo("Attention", "Vous n'avez rien sélectionné")


class MenuMain(tk.Menu):
    """ Class contenant le menu"""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent
        self.file_menu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Fichier", underline=0, menu=self.file_menu)
        self.file_menu.add_command(label="Archivage", underline=1, command=self.parent.archive_popup_window)
        self.file_menu.add_command(label="Exit", underline=2, command=self.quit)


class App(tk.Tk):
    """
    Class principal de Tk
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.menubar = MenuMain(self)
        self.config(menu=self.menubar)
        self.archive_popup = None

        self.title("Gestion de l'export des résultats de traction")
        # self.geometry('640x480')
        # self.maxsize(800, 600)
        # self.minsize(300, 400)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # MainApplication(self).pack(side="top", fill="both", expand=True)
        self.main_application = MainApplication(self)
        self.main_application.grid(row=0, column=0, sticky='nswe')
        # OtherFrame(self).pack(side="bottom")

    # Pour créer l'instance de la class ArchivePopup toplevel
    def archive_popup_window(self):
        if self.archive_popup is None:
            self.archive_popup = ArchivePopup()
        else:
            self.archive_popup.deiconify()
        self.archive_popup.bind("<Destroy>", self._archive_popup_window_destroyed)

    # Permet de remettre a None archive_popup et de faire une action a la fermeture de la fenêtre
    def _archive_popup_window_destroyed(self, event):
        if event.widget == self.archive_popup:
            self.archive_popup = None

    # afficher les erreurs
    def report_callback_exception(self, exc, val, tb):
        showerror("Error", message=str(val))


def get_result_date_list():
    """ Fonction qui récupère la liste des dossiers export """
    os.chdir(config.get('ResultsFolder', 'SuiviPath'))
    result_list = ["En attente export"]
    list_folder = [name for name in os.listdir(".") if os.path.isdir(name)]
    # On trie la liste des dossiers en fonction de la date, plus récent en 1er
    list_folder.sort(key=lambda x: datetime.strptime(x.split(' ')[2], "%d-%m-%y"), reverse=True)
    result_list.extend(list_folder)
    return result_list


def xml_pdf_to_tiff(essais_id, pdf_name):
    xml_encoding = 'ISO-8859-1'
    # On créer le nom du fichier xml et on définit ou l'enregistrer
    xml_name = "\IC_PL_ESS_RES_" + essais_id[1] + "_" + essais_id[2] + "_" + essais_id[3] + "_" + essais_id[4] + "_" + \
               essais_id[5] + ".xml"
    xml_path_to_save = config.get('Annexe', 'SaveXMLTiffFolder') + xml_name

    # On récupere l'emplacement du script pour ensuite chercher les templates
    script_path = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    path_to_xml_essais = os.path.join(script_path, 'Xml Template', 'xml_template_essais.xml')
    path_to_xml_eprouvette = os.path.join(script_path, 'Xml Template', 'xml_template_eprouvette.xml')
    path_to_xml_parametre = os.path.join(script_path, 'Xml Template', 'xml_template_parametre.xml')
    # import des templates
    # Essais
    root_essais = et.parse(path_to_xml_essais).getroot()
    # Eprouvette
    root_eprouvette = et.parse(path_to_xml_eprouvette).getroot()
    # Parametre
    root_parametre = et.parse(path_to_xml_parametre).getroot()

    # Dans un premier temps on remplie la partie parametre
    # NumPara = 907 pour annexe traction et micro
    root_parametre.find("./NumPara").text = "907"
    # pas de valuePara
    # root_parametre.find("./ValuePara").text = "ValuePara"
    # Ici on doit mettre le nom du fichier
    root_parametre.find("./ValueParaT").text = pdf_name
    # Pour sequence j'ai mis 1 pour le moment
    root_parametre.find("./SequenceResult").text = "1"
    root_parametre.find("./SequenceEssEpr").text = "1"

    # insert para dans eprouvette
    root_eprouvette.find("./Parametres").insert(0, root_parametre)
    # eprouvette_para.insert(0, root_parametre)

    # On complete eprouvette
    root_eprouvette.find("./SeqEssais").text = essais_id[5]

    # insert eprouvette dans essais
    root_essais.find("./__Essai/Eprouvettes").insert(0, root_eprouvette)

    # On complete essais
    root_essais.find("./__Essai/Source").text = "LABO_IC"
    root_essais.find("./__Essai/TimeStamp").text = datetime.now().strftime('%Y%m%d%H%M%S%f')
    root_essais.find("./__Essai/NoCommande").text = essais_id[1]
    root_essais.find("./__Essai/NoPoste").text = essais_id[2]
    root_essais.find("./__Essai/Batch").text = essais_id[3]
    root_essais.find("./__Essai/SequenceLoc").text = essais_id[4]

    et.indent(root_essais)
    et.ElementTree(root_essais).write(xml_path_to_save, pretty_print=True, encoding=xml_encoding)


def pdf_to_tiff(path_to_pdf, essais_id):
    """ Conversion des PDF en TIFF"""
    tiff_name = "\TIFF_" + essais_id[1] + "_" + essais_id[2] + "_" + essais_id[3] + "_" + essais_id[4] + "_" + \
                essais_id[5] + ".tiff"
    path_export_tiff = config.get('Annexe', 'SaveXMLTiffFolder') + tiff_name
    args = [
        "ps2pdf",  # actual value doesn't matter
        "-dNOPAUSE", "-dBATCH", "-dSAFER",
        "-r" + config.get('TIFF', 'Resolution'),
        "-sDEVICE=" + config.get('TIFF', 'Device'),
        "-sCompression=" + config.get('TIFF', 'Compression'),
        "-sOutputFile=" + path_export_tiff,
        path_to_pdf
    ]

    ghostscript.Ghostscript(*args)

    return tiff_name


if __name__ == "__main__":
    # Todo : Vérifier que la structure des dossier est ok, sinon voir pour créer
    # Vérification si le fichier de config est bien présent
    # Recuperation de la configuration
    if os.path.exists('config.ini'):
        config = ConfigParser()
        config.read('config.ini')
        app = App()
        # MainApplication(root).pack(side="top", fill="both", expand=True)
        app.mainloop()
    else:
        showerror("Error", message="Le fichier config.ini n'est pas présent.")
        quit()
