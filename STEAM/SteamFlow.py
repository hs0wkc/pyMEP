import tkinter as tk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from math import pi, sqrt
from csv import DictReader
from PIL import Image
from lib.pyCSV import LibFile, readall_csv2

class SteamFlow(Ctk.CTkFrame):
    def NPS_changed(self, e):
        OD = float(self.ODList[self.NPS.index(self.cmbNPS.get())])
        thk = float(self.THKList[self.NPS.index(self.cmbNPS.get())])
        self.InsideDiameter = (OD - 2 * thk) / 1000
        self.btnNPS.configure(text='id {:.3f}'.format(self.InsideDiameter))

    def NPS_click(self):
        F = self.tbFlow.get()
        V = self.tbVelocity.get()
        Vg = float(self.steam_vg[self.cmbPressure.get()])
        D = round(sqrt((F * Vg * 4) / (3600 * pi * V)), 5)
        for i in range(len(self.NPS)):
            OD = float(self.ODList[i])
            thk = float(self.THKList[i])
            if ((OD - 2 * thk) / 1000) >= D:
                break
        self.cmbNPS.set(self.NPS[i])
        self.NPS_changed(None)

    def PS_changed(self, e):
        self.THKList = readall_csv2(self.CSV_PIPETABLE, self.NPS, 'nps', self.cmbPS.get())
        self.NPS_changed(None)

    def SteamVelocity_click(self):
        F = self.tbFlow.get()
        D = self.InsideDiameter
        Vg = float(self.steam_vg[self.cmbPressure.get()])
        SteamVelocity = (F * Vg * 4) / (3600 * pi * (D * D))
        self.tbVelocity.set(round(SteamVelocity, 2))

    def SteamFlowrate_click(self):
        V = self.tbVelocity.get()
        D = self.InsideDiameter
        Vg = float(self.steam_vg[self.cmbPressure.get()])
        SteamFlowrate = (V * 3600 * pi * (D * D)) / (Vg * 4)
        self.tbFlow.set(round(SteamFlowrate, 2))
        # print(V,D, Vg, SteamFlowrate, self.cmbPressure.get())

    def __init__(self, master, NPS, CSV_PIPETABLE, ODList, THKList, steam_vg):
        super().__init__(master)
        self.InsideDiameter = 0.05248
        self.tbVelocity = tk.DoubleVar()
        self.tbVelocity.set(25.0)
        self.tbFlow = tk.DoubleVar()
        self.tbFlow.set(520.53)
        self.NPS = NPS
        self.CSV_PIPETABLE = CSV_PIPETABLE
        self.ODList = ODList
        self.THKList = THKList
        self.steam_vg = steam_vg

        Ctk.CTkLabel(self, text='Pipe Size (NPS)').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
        self.cmbNPS = Ctk.CTkComboBox(self, values=NPS, width=100, justify='right', command=self.NPS_changed)
        self.cmbNPS.grid(column=1, row=0, sticky=tk.W, padx=5, pady=(15, 3))
        self.cmbNPS.set('50 mm')
        self.btnNPS = Ctk.CTkButton(self, text='id 0.052', width=80, command=self.NPS_click)
        self.btnNPS.grid(column=3, sticky=tk.W, row=0, padx=5, pady=(15, 3))

        Ctk.CTkLabel(self, text='Pipe Schedule').grid(column=0, row=1, sticky=tk.E, padx=5, pady=3)
        self.cmbPS = Ctk.CTkComboBox(self, values=['40', '80'], width=100, justify='right', command=self.PS_changed)
        self.cmbPS.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
        self.cmbPS.set('40')

        Ctk.CTkLabel(self, text='Steam Pressure').grid(column=0, row=2, sticky=tk.E, padx=5, pady=3)
        self.cmbPressure = Ctk.CTkComboBox(self, width=100, justify='right')
        self.cmbPressure.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
        # self.cmbPressure.configure(values=list(steam_pressure.keys())[1:])
        self.cmbPressure.set('7')
        CTkScrollableDropdown(self.cmbPressure, values=list(steam_vg.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='bar.g').grid(column=2, row=2, sticky=tk.W)

        Ctk.CTkLabel(self, text='Velocity').grid(column=0, row=3, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbVelocity, width=100, justify='right').grid(column=1, row=3, sticky=tk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='m/s').grid(column=2, row=3, sticky=tk.W)
        Ctk.CTkButton(self, text='Velocity', width=80, command=self.SteamVelocity_click).grid(column=3, sticky=tk.W, row=3, padx=5, pady=3)

        Ctk.CTkLabel(self, text='Flow').grid(column=0, row=4, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbFlow, width=100, justify='right').grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='kg/hr').grid(column=2, row=4, sticky=tk.W)
        Ctk.CTkButton(self, text='Flowrate', width=80, command=self.SteamFlowrate_click).grid(column=3, sticky=tk.W, row=4, padx=5, pady=3)

        # ttk.Separator(self, orient='horizontal').grid(column=0, columnspan=4, row=5, sticky='ew', padx=15, pady=10)
        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=5, sticky=tk.EW, padx=15, pady=15)

        formula_image = Ctk.CTkImage(light_image=Image.open('images/Formula.jpg'), size=(340, 90))
        Ctk.CTkLabel(self, image=formula_image, text='').grid(column=0, columnspan=4, row=6, padx=10, pady=5, sticky=tk.EW)

if __name__ == "__main__":

    class MainWindow(Ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title("Steam Flow")
            self.geometry("367x315")
            self.resizable(False, False)

            self.SteamFlow_frame = SteamFlow(self, NPS, CSV_PIPETABLE, ODList, THKList, steam_vg)
            self.SteamFlow_frame.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)

    NPS = ('15 mm', '20 mm', '25 mm', '32 mm', '40 mm', '50 mm', '65 mm', '80 mm', '100 mm', '125 mm', '150 mm', '200 mm', '250 mm', '300 mm')
    CSV_STEAMTABLE = LibFile('SteamTable.csv')
    CSV_PIPETABLE = LibFile('PipeThickness.csv')
    ODList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', 'OD')
    THKList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', '40')
    steam_vg = {}
    with open(CSV_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            steam_vg[row['Pressure']] = row['Vg']

    app = MainWindow()
    app.mainloop()
