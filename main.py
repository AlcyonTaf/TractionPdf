# Use Tkinter for python 2, tkinter for python 3
import tkinter as tk
from tkinter import ttk, Text
from tkinter.messagebox import showinfo


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="red", *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)


        TreeView(self).grid(row=0, column=1, sticky='news')
        Details(self).grid(row=1, column=1, sticky='news')

        # self.label = tk.Label(self, text="Test text")
        # self.label.grid(row=2, column=1)


class TreeView(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # define columns
        columns = ('first_name', 'last_name', 'email')

        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        self.tree.heading('first_name', text='First Name')
        self.tree.heading('last_name', text='Last Name')
        self.tree.heading('email', text='Email')

        # generate sample data
        contacts = []
        for n in range(1, 100):
            contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))

        # add data to the treeview
        for contact in contacts:
            self.tree.insert('', tk.END, values=contact)
        # self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=0, column=0, sticky='nesw')

    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']
            # show a message
            showinfo(title='Information', message=','.join(record))
        # add a scrollbar
        # scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        # tree.configure(yscroll=scrollbar.set)
        # scrollbar.grid(row=0, column=1, sticky='ns')


class Details(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, bg="blue", *args, **kwargs)
        self.parent = parent
        self.configure(background='blue')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        #self.label = tk.Label(self, text="Test text2")
        #self.label.pack()
        text = Text(self)
        text.grid(row=0, column=0, sticky='news')


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

        #MainApplication(self).pack(side="top", fill="both", expand=True)
        MainApplication(self).grid(row=0, column=0, sticky='nswe')
        # OtherFrame(self).pack(side="bottom")


def hello():
    print("hello!")


if __name__ == "__main__":
    app = App()
    # MainApplication(root).pack(side="top", fill="both", expand=True)
    app.mainloop()
