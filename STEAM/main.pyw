import os
from math import pi, sqrt
import webbrowser
import tkinter as tk
from tkinter import ttk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from csv import DictReader
from PIL import Image
from pyCSV import ExtensionPath, readall_csv2

class BoilerRating(Ctk.CTkFrame):
    def EvaporationRate(self):
        B = float(steam_hg[self.cmbPressure.get()])  # Specific enthalpy of steam at operating pressure (hg)
        C = float(water_temp[self.cmbTemperature.get()])  # Specific enthalpy of water at feedwater temperature (hf)
        self.tbEvaporationRate.set(round(A / (B - C) * self.tbEquivalentOutputKG.get() if self.rbtnRating.get() == 0 else 3600 / (B - C) * self.tbEquivalentOutputKW.get(), 2))

    def __init__(self, master):
        super().__init__(master)
        self.tbEquivalentOutputKG = Ctk.DoubleVar()
        self.tbEquivalentOutputKG.set(2500)
        self.tbEquivalentOutputKW = Ctk.DoubleVar()
        self.tbEquivalentOutputKW.set(1800)
        self.rbtnRating = Ctk.IntVar()
        self.tbEvaporationRate = Ctk.DoubleVar()
        self.tbEvaporationRate.set(2320.58)

        Ctk.CTkLabel(self, text='Operating Pressure').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
        self.cmbPressure = Ctk.CTkComboBox(self, width=80, justify='right')
        self.cmbPressure.grid(column=1, row=0, sticky=Ctk.W, padx=5, pady=(15, 3))
        self.cmbPressure.set('8')
        CTkScrollableDropdown(self.cmbPressure, values=list(steam_hg.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='bar.g').grid(column=2, row=0, sticky=Ctk.W, padx=5, pady=(15, 3))

        Ctk.CTkLabel(self, text='Feedwater Temperature').grid(column=0, row=1, sticky=Ctk.E, padx=(15, 5), pady=3)
        self.cmbTemperature = Ctk.CTkComboBox(self, width=80, justify='right')
        self.cmbTemperature.grid(column=1, row=1, sticky=Ctk.W, padx=5, pady=3)
        self.cmbTemperature.set('80')
        CTkScrollableDropdown(self.cmbTemperature, values=list(water_temp.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='°C').grid(column=2, row=1, sticky=Ctk.W, padx=5)

        Ctk.CTkLabel(self, text='Boiler Equivalent Output').grid(column=0, row=2, sticky=Ctk.E, padx=(20, 5), pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKG, width=80, justify='right').grid(column=1, row=2, sticky=Ctk.W, padx=5, pady=3)
        Ctk.CTkRadioButton(self, text='kg/h Rating', value=0, variable=self.rbtnRating, command=self.EvaporationRate).grid(column=2, row=2, sticky=Ctk.W, padx=5, pady=3)

        Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKW, width=80, justify='right').grid(column=1, row=3, sticky=Ctk.W, padx=5, pady=3)
        Ctk.CTkRadioButton(self, text='kW Rating', value=1, variable=self.rbtnRating, command=self.EvaporationRate).grid(column=2, row=3, sticky=Ctk.W, padx=5, pady=3)

        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=4, sticky='ew', padx=10, pady=(10, 20))

        Ctk.CTkLabel(self, text='Boiler Evaporation Rate').grid(column=0, row=5, sticky=Ctk.E, padx=5, pady=(3, 15))
        Ctk.CTkEntry(self, textvariable=self.tbEvaporationRate, width=80, justify='right', state=Ctk.DISABLED, border_color='green').grid(column=1, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))
        Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))

        ie_image = Ctk.CTkImage(light_image=Image.open('images/ie.png'), size=(30, 30))
        link = Ctk.CTkLabel(self, image=ie_image, text='', cursor='hand2')
        link.grid(column=2, row=5, sticky=tk.E, padx=15, pady=(3, 15))
        link.bind("<Button-1>", lambda e: webbrowser.open("https://www.spiraxsarco.com/learn-about-steam/the-boiler-house/boiler-ratings?sc_lang=en-GB"))

class SteamFlow(Ctk.CTkFrame):
    def NPS_changed(self, e):
        OD = float(ODList[NPS.index(self.cmbNPS.get())])
        thk = float(THKList[NPS.index(self.cmbNPS.get())])
        self.InsideDiameter = (OD - 2 * thk) / 1000
        # self.btnNPS['text'] = 'id {:.3f}'.format(self.InsideDiameter)
        self.btnNPS.configure(text='id {:.3f}'.format(self.InsideDiameter))

    def NPS_click(self):
        F = self.tbFlow.get()
        V = self.tbVelocity.get()
        Vg = float(steam_vg[self.cmbPressure.get()])
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
        Vg = float(steam_vg[self.cmbPressure.get()])
        SteamVelocity = (F * Vg * 4) / (3600 * pi * (D * D))
        self.tbVelocity.set(round(SteamVelocity, 2))

    def SteamFlowrate_click(self):
        V = self.tbVelocity.get()
        D = self.InsideDiameter
        Vg = float(steam_vg[self.cmbPressure.get()])
        SteamFlowrate = (V * 3600 * pi * (D * D)) / (Vg * 4)
        self.tbFlow.set(round(SteamFlowrate, 2))
        # print(V,D, Vg, SteamFlowrate, self.cmbPressure.get())

    def __init__(self, master):
        super().__init__(master)
        self.InsideDiameter = 0.05248
        self.tbVelocity = tk.DoubleVar()
        self.tbVelocity.set(25.0)
        self.tbFlow = tk.DoubleVar()
        self.tbFlow.set(520.53)

        Ctk.CTkLabel(self, text='Pipe Size (NPS)').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
        self.cmbNPS = Ctk.CTkComboBox(self, values=NPS, width=100, justify='right', command=self.NPS_changed)
        self.cmbNPS.grid(column=1, row=0, sticky=tk.W, padx=5, pady=(15, 3))
        self.cmbNPS.set('50 mm')
        self.btnNPS = Ctk.CTkButton(self, text='id 0.052', width=80, command=self.NPS_click)
        self.btnNPS.grid(column=3, sticky=tk.W, row=0, padx=(0, 5), pady=(15, 3))

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
        Ctk.CTkButton(self, text='Velocity', width=80, command=self.SteamVelocity_click).grid(column=3, sticky=tk.W, row=3, padx=(0, 5), pady=3)

        Ctk.CTkLabel(self, text='Flow').grid(column=0, row=4, sticky=tk.E, padx=5, pady=3)
        Ctk.CTkEntry(self, textvariable=self.tbFlow, width=100, justify='right').grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
        Ctk.CTkLabel(self, text='kg/hr').grid(column=2, row=4, sticky=tk.W)
        Ctk.CTkButton(self, text='Flowrate', width=80, command=self.SteamFlowrate_click).grid(column=3, sticky=tk.W, row=4, padx=(0, 5), pady=3)

        # ttk.Separator(self, orient='horizontal').grid(column=0, columnspan=4, row=5, sticky='ew', padx=15, pady=10)
        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=5, sticky='ew', padx=15, pady=10)

        formula_image = Ctk.CTkImage(light_image=Image.open('images/Formula.png'), size=(340, 90))
        # formula_image = Ctk.CTkImage(light_image=Image.open(os.path.join(scriptpath, 'images/Formula.jpg')), size=(340, 90))
        canvas = Ctk.CTkLabel(self, image=formula_image, text='', cursor='hand2', corner_radius=15)
        canvas.grid(column=0, columnspan=4, row=6, padx=10, sticky='ew')
        canvas.bind("<Button-1>", lambda e: webbrowser.open("https://www.spiraxsarco.com/learn-about-steam/steam-distribution/pipes-and-pipe-sizing?sc_lang=en-GB"))

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
    def ShowMainFrame(self):
        for i in self.menu_frame:
            i.grid_forget()
        self.menu_frame[self.main_menu.index(self.SideMenu_frame.get())].grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Steam Engineering Toolbox')
        self.iconbitmap('images/logo.ico')
        self.geometry("510x300")
        self.grid_columnconfigure(1, weight=1)
        # self.resizable(False, False)

        self.main_menu = ["Boiler Rating", "Steam Flow"]
        self.SideMenu_frame = SideMenuFrame(self, title="Main Menu", menus=self.main_menu, commander=self.ShowMainFrame)
        self.SideMenu_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        self.menu_frame = []
        self.BoilerRating_frame = BoilerRating(self)
        self.menu_frame.append(self.BoilerRating_frame)
        self.SteamFlow_frame = SteamFlow(self)
        self.menu_frame.append(self.SteamFlow_frame)
        self.BoilerRating_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

if __name__ == "__main__":
    NPS = ('15 mm', '20 mm', '25 mm', '32 mm', '40 mm', '50 mm', '65 mm', '80 mm', '100 mm', '125 mm', '150 mm', '200 mm', '250 mm', '300 mm')
    CSV_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'SteamTable.csv'))
    CSV_WATER_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'WaterTable.csv'))
    CSV_PIPETABLE = os.path.normpath(os.path.join(ExtensionPath(), 'PipeThickness.csv'))
    ODList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', 'OD')
    THKList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', '40')
    steam_hg = {}
    steam_vg = {}
    with open(CSV_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            steam_hg[row['Pressure']] = row['hg(j)']
            steam_vg[row['Pressure']] = row['Vg']
    water_temp = {}
    with open(CSV_WATER_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            water_temp[row['Temp']] = row['hf(j)']

    # A : Specific enthalpy of evaporation at atmospheric pressure (hfg)
    A = float(readall_csv2(CSV_STEAMTABLE, ['1'], 'Pressure', 'hfg(j)')[0])

    app = MainWindow()
    app.mainloop()
