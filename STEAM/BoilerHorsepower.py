import tkinter as tk
import customtkinter as Ctk

class BoilerHorsepower(Ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.tbEquivalentOutputKG = Ctk.DoubleVar()
        self.tbEquivalentOutputKG.set(1000)
        self.tbBoilerHorsepower = Ctk.StringVar()
        self.tbBoilerHorsepower.set('421.74')

        Ctk.CTkLabel(self, text='Boiler Equivalent Output').grid(column=0, row=0, sticky=tk.E, padx=(20, 5), pady=(15, 3))
        self.i = Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKG, width=80, justify='right')
        self.i.grid(column=1, row=0, sticky=Ctk.W, padx=5, pady=(15, 3))
        self.i.bind('<Return>', lambda master: self.tbBoilerHorsepower.set('{:,.2f}'.format(self.tbEquivalentOutputKG.get() / 15.65 * 6.6)))
        Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=0, sticky=Ctk.W, padx=(5, 10), pady=(15, 3))

        Ctk.CTkLabel(self, text='แรงม้าเสียภาษี').grid(column=0, row=1, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbBoilerHorsepower, width=80, justify='right', state=Ctk.DISABLED, border_color='green').grid(column=1, row=1, sticky=Ctk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='HP').grid(column=2, row=1, sticky=Ctk.W, padx=5, pady=3)

        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=3, row=4, sticky=tk.EW, padx=10, pady=10)

        self.textbox = Ctk.CTkTextbox(master=self, corner_radius=5, height=112)
        self.textbox.grid(column=0, columnspan=3, row=5, padx=10, pady=5, sticky=tk.EW)
        self.textbox.insert("0.0", "1 แรงม้าหม้อไอน้ำ = 15.65 kg steam/hr\n1 แรงม้าหม้อไอน้ำ =  9.8095 kW\n1 แรงม้าหม้อไอน้ำ =  13.13 แรงม้าเครื่องยนต์")
        self.textbox.configure(state="disabled")

if __name__ == "__main__":

    class MainWindow(Ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("วิธีคำนวณแรงม้าเสียภาษี")
            self.geometry("298x225")
            self.resizable(False, False)

            self.BoilerHorsepower_frame = BoilerHorsepower(self)
            self.BoilerHorsepower_frame.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)

    app = MainWindow()
    app.mainloop()
