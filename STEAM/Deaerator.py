import os
import tkinter as tk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from csv import DictReader
from lib.pyCSV import LibFile, readall_csv2

class Deaerator(Ctk.CTkFrame):
    def HeatBalance(self, e):
        B = float(self.steam_hg[self.cmbPressure.get()])  # Specific enthalpy of steam at operating pressure (hg)
        C = float(self.water_temp[self.cmbTemperaturein.get()])  # Specific enthalpy of water at initial feedwater temperature (hf)
        EvaporationFactor = self.A / (B - C) * self.tbEquivalentOutputKG.get()
        h2 = float(self.water_temp[self.cmbTemperatureout.get()])  # Specific enthalpy of water at final feedwater temperature (hf)
        self.tbSteamInjected.set('{:,.2f}'.format(EvaporationFactor * (h2 - C) / (B - h2)))

    def __init__(self, master, steam_hg, water_temp, A):
        super().__init__(master)
        self.tbEquivalentOutputKG = Ctk.DoubleVar()
        self.tbEquivalentOutputKG.set(10000)
        self.rbtnRating = Ctk.IntVar()
        self.tbSteamInjected = Ctk.StringVar()
        self.tbSteamInjected.set('334.66')
        self.steam_hg = steam_hg
        self.water_temp = water_temp
        self.A = A

        Ctk.CTkLabel(self, text='Boiler Pressure').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
        self.cmbPressure = Ctk.CTkComboBox(self, width=80, justify='right')
        self.cmbPressure.grid(column=1, row=0, sticky=Ctk.W, padx=5, pady=(15, 3))
        self.cmbPressure.set('10')
        CTkScrollableDropdown(self.cmbPressure, values=list(steam_hg.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='bar.g').grid(column=2, row=0, sticky=Ctk.W, padx=5, pady=(15, 3))

        Ctk.CTkLabel(self, text='Feedwater Temperature (IN)').grid(column=0, row=1, sticky=Ctk.E, padx=(15, 5), pady=3)
        self.cmbTemperaturein = Ctk.CTkComboBox(self, width=80, justify='right')
        self.cmbTemperaturein.grid(column=1, row=1, sticky=Ctk.W, padx=5, pady=3)
        self.cmbTemperaturein.set('85')
        CTkScrollableDropdown(self.cmbTemperaturein, values=list(water_temp.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='°C').grid(column=2, row=1, sticky=Ctk.W, padx=5)

        Ctk.CTkLabel(self, text='Feedwater Temperature (OUT)').grid(column=0, row=2, sticky=Ctk.E, padx=(15, 5), pady=3)
        self.cmbTemperatureout = Ctk.CTkComboBox(self, width=80, justify='right')
        self.cmbTemperatureout.grid(column=1, row=2, sticky=Ctk.W, padx=5, pady=3)
        self.cmbTemperatureout.set('105')
        CTkScrollableDropdown(self.cmbTemperatureout, values=list(water_temp.keys())[1:], justify="left", height=600)
        Ctk.CTkLabel(self, text='°C').grid(column=2, row=2, sticky=Ctk.W, padx=5)

        Ctk.CTkLabel(self, text='Boiler Equivalent Output').grid(column=0, row=3, sticky=Ctk.E, padx=(20, 5), pady=3)
        self.i = Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKG, width=80, justify='right')
        self.i.grid(column=1, row=3, sticky=Ctk.W, padx=5, pady=3)
        self.i.bind('<Return>', self.HeatBalance)
        Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=3, sticky=Ctk.W, padx=5)

        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=4, sticky=tk.EW, padx=10, pady=(10, 20))

        Ctk.CTkLabel(self, text='Steam Required').grid(column=0, row=5, sticky=Ctk.E, padx=5, pady=(3, 15))
        Ctk.CTkEntry(self, textvariable=self.tbSteamInjected, width=80, justify='right', state=Ctk.DISABLED, border_color='green').grid(column=1, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))
        Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))

if __name__ == "__main__":

    class MainWindow(Ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title('Pressurised Deaerators')
            self.geometry("342x228")
            self.resizable(False, False)

            self.Deaerator_frame = Deaerator(self, steam_hg, water_temp, A)
            self.Deaerator_frame.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)

    CSV_STEAMTABLE = LibFile('SteamTable.csv')
    CSV_WATER_STEAMTABLE = LibFile('WaterTable.csv')
    steam_hg = {}
    with open(CSV_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            steam_hg[row['Pressure']] = row['hg(j)']
    water_temp = {}
    with open(CSV_WATER_STEAMTABLE) as f:
        reader = DictReader(f)
        for row in reader:
            water_temp[row['Temp']] = row['hf(j)']
    # A : Specific enthalpy of evaporation at atmospheric pressure (hfg)
    A = float(readall_csv2(CSV_STEAMTABLE, ['0'], 'Pressure', 'hfg(j)')[0])
    app = MainWindow()
    app.mainloop()
