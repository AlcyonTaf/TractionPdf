import tkinter as tk

class Main(tk.Tk):
    def __init__(self):
        super().__init__()
        self.sub_app_one = None
        b1 = tk.Button(self, text="Open Sub App One", command=self.sub_app_one_open)
        b1.pack(padx=20, pady=20)

    def sub_app_one_open(self):
        if self.sub_app_one is None:
            self.sub_app_one = Sub_app_one(self)
        else:
            self.sub_app_one.deiconify()
        self.sub_app_one.bind("<Destroy>", self._child_destroyed)

    def _child_destroyed(self, event):
        if event.widget == self.sub_app_one:
            print("sub_app_one has been destroyed")
            self.sub_app_one = None

class Sub_app_one(tk.Toplevel):
    def __init__(self, main_app):
        self.main_app = main_app
        super().__init__(main_app)
        label = tk.Label(self, text="This is sub app one")
        label.pack(padx=50, pady=50)

main = Main()
main.mainloop()