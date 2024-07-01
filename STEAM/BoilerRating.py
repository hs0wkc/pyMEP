import os
import tkinter as tk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from csv import DictReader
from lib.pyCSV import LibFile, readall_csv2

class BoilerRating(Ctk.CTkFrame):
    def EvaporationRate(self):
        B = float(self.steam_hg[self.cmbPressure.get()])  # Specific enthalpy of steam at operating pressure (hg)
        C = float(self.water_temp[self.cmbTemperature.get()])  # Specific enthalpy of water at feedwater temperature (hf)
        self.tbEvaporationRate.set('{:,.2f}'.format(self.A / (B - C) * self.tbEquivalentOutputKG.get() if self.rbtnRating.get() == 0 else 3600 / (B - C) * self.tbEquivalentOutputKW.get()))

    def __init__(self, master, steam_hg, water_temp, A):
        super().__init__(master)
        self.tbEquivalentOutputKG = Ctk.DoubleVar()
        self.tbEquivalentOutputKG.set(2500)
        self.tbEquivalentOutputKW = Ctk.DoubleVar()
        self.tbEquivalentOutputKW.set(1800)
        self.rbtnRating = Ctk.IntVar()
        self.tbEvaporationRate = Ctk.StringVar()
        self.tbEvaporationRate.set('2,320.58')
        self.steam_hg = steam_hg
        self.water_temp = water_temp
        self.A = A

        Ctk.CTkLabel(self, text='Boiler Pressure').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15, 3))
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

        tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=4, sticky=tk.EW, padx=10, pady=(10, 20))

        Ctk.CTkLabel(self, text='Boiler Evaporation Rate').grid(column=0, row=5, sticky=Ctk.E, padx=5, pady=(3, 15))
        Ctk.CTkEntry(self, textvariable=self.tbEvaporationRate, width=80, justify='right', state=Ctk.DISABLED, border_color='green').grid(column=1, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))
        Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=5, sticky=Ctk.W, padx=5, pady=(3, 15))

        # ie_image = Ctk.CTkImage(light_image=Image.open('images/ie.png'), size=(30, 30))
        # link = Ctk.CTkLabel(self, image=ie_image, text='', cursor='hand2')
        # link.grid(column=2, row=5, sticky=tk.E, padx=15, pady=(3, 15))
        # link.bind("<Button-1>", lambda e: webbrowser.open("https://www.spiraxsarco.com/learn-about-steam/the-boiler-house/boiler-ratings?sc_lang=en-GB"))

if __name__ == "__main__":

    class MainWindow(Ctk.CTk):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title('Boiler Ratings')
            self.geometry("375x228")
            self.resizable(False, False)

            self.BoilerRating_frame = BoilerRating(self, steam_hg, water_temp, A)
            self.BoilerRating_frame.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)

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
