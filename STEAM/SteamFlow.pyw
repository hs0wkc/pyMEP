import os
import webbrowser
import tkinter as tk
from tkinter import ttk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from math import pi, sqrt
from csv import DictReader
from PIL import Image
from pyCSV import ExtensionPath, readall_csv2

class SteamFlow(Ctk.CTk):
    def NPS_changed(self, e):
        OD = float(ODList[NPS.index(self.cmbNPS.get())])
        thk = float(THKList[NPS.index(self.cmbNPS.get())])
        self.InsideDiameter = (OD - 2 * thk) / 1000
        # self.btnNPS['text'] = 'id {:.3f}'.format(self.InsideDiameter)
        self.btnNPS.configure(text='id {:.3f}'.format(self.InsideDiameter))

    def NPS_click(self):
        F = self.tbFlow.get()
        V = self.tbVelocity.get()
        Vg = float(steam_pressure[self.cmbPressure.get()])
        D = round(sqrt((F * Vg * 4) / (3600 * pi * V)), 5)
        for i in range(len(NPS)):
            OD = float(ODList[i])
            thk = float(THKList[i])
            if ((OD - 2 * thk) / 1000) >= D:
                break
        self.cmbNPS.set(NPS[i])
        self.NPS_changed(None)

    def PS_changed(self, e):
        global THKList
        THKList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', self.cmbPS.get())
        self.NPS_changed(None)

    def SteamVelocity_click(self):
        F = self.tbFlow.get()
        D = self.InsideDiameter
        Vg = float(steam_pressure[self.cmbPressure.get()])
        SteamVelocity = (F * Vg * 4) / (3600 * pi * (D * D))
        self.tbVelocity.set(round(SteamVelocity, 2))

    def SteamFlowrate_click(self):
        V = self.tbVelocity.get()
        D = self.InsideDiameter
        Vg = float(steam_pressure[self.cmbPressure.get()])
        SteamFlowrate = (V * 3600 * pi * (D * D)) / (Vg * 4)
        self.tbFlow.set(round(SteamFlowrate, 2))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Steam Flow")
        self.geometry("400x300")
        self.configure(fg_color='white')
        self.resizable(False, False)
        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=4)

        self.InsideDiameter = 0.05248
        self.tbVelocity = tk.DoubleVar()
        self.tbVelocity.set(25.0)
        self.tbFlow = tk.DoubleVar()
        self.tbFlow.set(520.53)

        Ctk.CTkLabel(self, text='Pipe Size (NPS)').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
        self.cmbNPS = Ctk.CTkComboBox(self, values=NPS, width=100, justify='right', command=self.NPS_changed)
        self.cmbNPS.grid(column=1, row=0, sticky=tk.W, padx=5, pady=(15, 3))
        self.cmbNPS.set('50 mm')
        self.btnNPS = Ctk.CTkButton(self, text='id 0.052', width=100, command=self.NPS_click)
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
        CTkScrollableDropdown(self.cmbPressure, values=list(steam_pressure.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='bar.g').grid(column=2, row=2, sticky=tk.W)

        Ctk.CTkLabel(self, text='Velocity').grid(column=0, row=3, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbVelocity, width=100, justify='right').grid(column=1, row=3, sticky=tk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='m/s').grid(column=2, row=3, sticky=tk.W)
        Ctk.CTkButton(self, text='Velocity', width=100, command=self.SteamVelocity_click).grid(column=3, sticky=tk.W, row=3, padx=5, pady=3)

        Ctk.CTkLabel(self, text='Flow').grid(column=0, row=4, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbFlow, width=100, justify='right').grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='kg/hr').grid(column=2, row=4, sticky=tk.W)
        Ctk.CTkButton(self, text='Flowrate', width=100, command=self.SteamFlowrate_click).grid(column=3, sticky=tk.W, row=4, padx=5, pady=3)

        ttk.Separator(self, orient='horizontal').grid(column=0, columnspan=4, row=5, sticky='ew', padx=15, pady=10)

        formula_image = Ctk.CTkImage(light_image=Image.open('images/Formula.jpg'), size=(340, 90))
        # formula_image = Ctk.CTkImage(light_image=Image.open(os.path.join(scriptpath, 'images/Formula.jpg')), size=(340, 90))
        canvas = Ctk.CTkLabel(self, image=formula_image, text='', cursor='hand2')
        canvas.grid(column=0, columnspan=4, row=6, sticky='ew')
        canvas.bind("<Button-1>", lambda e: webbrowser.open("https://www.spiraxsarco.com/learn-about-steam/steam-distribution/pipes-and-pipe-sizing?sc_lang=en-GB"))

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.abspath(__file__))
    NPS = ('15 mm', '20 mm', '25 mm', '32 mm', '40 mm', '50 mm', '65 mm', '80 mm', '100 mm', '125 mm', '150 mm', '200 mm', '250 mm', '300 mm')
    CSV_PIPETABLE = os.path.normpath(os.path.join(ExtensionPath(), 'PipeThickness.csv'))
    CSV_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'SteamTable.csv'))
    ODList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', 'OD')
    THKList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', '40')
    steam_pressure = {}
    with open(CSV_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            steam_pressure[row['Pressure']] = row['Vg']
    Ctk.set_appearance_mode("light")

    app = SteamFlow()
    app.mainloop()
