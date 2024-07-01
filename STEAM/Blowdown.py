import tkinter as tk
import customtkinter as Ctk

class Blowdown(Ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

if __name__ == "__main__":
    class MainWindow(Ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Blowdown")
            self.geometry("367x315")
            self.resizable(False, False)

            self.Blowdown_frame = Blowdown(self)
            self.Blowdown_frame.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)

    app = MainWindow()
    app.mainloop()