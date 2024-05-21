import customtkinter as Ctk

class Option1Frame(Ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.title = Ctk.CTkLabel(self, text='Op1', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

class Option2Frame(Ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.title = Ctk.CTkLabel(self, text='Op2', fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

class SideMenuFrame(Ctk.CTkFrame):
    def __init__(self, master, title, menus, commander):
        super().__init__(master)
        self.variable = Ctk.StringVar(value=menus[0])
        self.title = Ctk.CTkLabel(self, text=title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        for i, value in enumerate(menus):
            radiobutton = Ctk.CTkRadioButton(self, text=value, value=value, variable=self.variable, command=commander)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")

    def get(self):
        return self.variable.get()

class MainWindow(Ctk.CTk):
    def MainFame(self):
        self.Option1_frame.grid_forget()
        self.Option2_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")
        print(self.SideMenu_frame.get())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Steam Engineering Toolbox')
        self.iconbitmap('images/logo.ico')
        self.geometry("400x250")
        self.grid_columnconfigure(1, weight=1)
        # self.resizable(False, False)

        main_menu = ["option 1", "option 2"]
        self.SideMenu_frame = SideMenuFrame(self, title="Main Menu", menus=main_menu, commander=self.MainFame)
        self.SideMenu_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        self.Option1_frame = Option1Frame(self)
        self.Option2_frame = Option2Frame(self)
        self.Option1_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
