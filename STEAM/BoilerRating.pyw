import os
import tkinter as tk
from tkinter import ttk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from csv import DictReader
from pyCSV import ExtensionPath, readall_csv2

class MainWindow(Ctk.CTk):
	def EvaporationRate(self):		
		B = float(steam_pressure[self.cmbPressure.get()])	# Specific enthalpy of steam at operating pressure (hg)		
		C = float(water_temp[self.cmbTemperature.get()])	# Specific enthalpy of water at feedwater temperature (hf)
		self.tbEvaporationRate.set(round(A/(B-C)*self.tbEquivalentOutputKG.get() if self.rbtnRating.get() == 0 else 3600/(B-C)*self.tbEquivalentOutputKW.get(), 2))

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.title('Boiler Ratings')
		self.geometry("370x220") 
		self.resizable(False, False)
		
		self.tbEquivalentOutputKG = tk.DoubleVar()
		self.tbEquivalentOutputKG.set(2500)
		self.tbEquivalentOutputKW = tk.DoubleVar()
		self.tbEquivalentOutputKW.set(1800)
		self.rbtnRating = tk.IntVar()
		self.tbEvaporationRate = tk.DoubleVar()
		self.tbEvaporationRate.set(2320.58)
		
		Ctk.CTkLabel(self, text='Operating Pressure').grid(column=0, row=0, sticky=tk.E, padx=5, pady=(15,3))
		self.cmbPressure = Ctk.CTkComboBox(self, width=80, justify='right')
		self.cmbPressure.grid(column=1, row=0, sticky=tk.W, padx=5, pady=(15,3))
		self.cmbPressure.set('8')
		CTkScrollableDropdown(self.cmbPressure, values=list(steam_pressure.keys())[1:], justify="left", height=600)
		Ctk.CTkLabel(self, text='bar.g').grid(column=2, row=0, sticky=tk.W, padx=5, pady=(15,3))		
		
		Ctk.CTkLabel(self, text='Feedwater Temperature').grid(column=0, row=1, sticky=tk.E, padx=5, pady=3)
		self.cmbTemperature = Ctk.CTkComboBox(self, width=80, justify='right')
		self.cmbTemperature.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
		self.cmbTemperature.set('80')
		CTkScrollableDropdown(self.cmbTemperature, values=list(water_temp.keys())[1:], justify="left", height=600)
		Ctk.CTkLabel(self, text='°C').grid(column=2, row=1, sticky=tk.W, padx=5)
		
		Ctk.CTkLabel(self, text='Boiler Equivalent Output').grid(column=0, row=2, sticky=tk.E, padx=(20,5), pady=3)
		Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKG, width=80, justify='right').grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
		Ctk.CTkRadioButton(self, text='kg/h Rating', value=0, variable=self.rbtnRating, command=self.EvaporationRate).grid(column=2, row=2, sticky=tk.W, padx=5, pady=3)
		
		Ctk.CTkEntry(self, textvariable=self.tbEquivalentOutputKW, width=80, justify='right').grid(column=1, row=3, sticky=tk.W, padx=5, pady=3)
		Ctk.CTkRadioButton(self, text='kW Rating', value=1, variable=self.rbtnRating, command=self.EvaporationRate).grid(column=2, row=3, sticky=tk.W, padx=5, pady=3)
		
		tk.Frame(self, bd=10, relief='sunken', height=1, bg="orange").grid(column=0, columnspan=4, row=4, sticky='ew', padx=10, pady=10)
		
		Ctk.CTkLabel(self, text='Boiler Evaporation Rate').grid(column=0, row=5, sticky=tk.E, padx=5, pady=3)
		Ctk.CTkEntry(self, textvariable=self.tbEvaporationRate, width=80, justify='right', state=tk.DISABLED).grid(column=1, row=5, sticky=tk.W, padx=5, pady=3)
		Ctk.CTkLabel(self, text='kg/h').grid(column=2, row=5, sticky=tk.W, padx=5, pady=3)

if __name__ == "__main__":
	CSV_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'SteamTable.csv'))
	CSV_WATER_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'WaterTable.csv'))
	steam_pressure = {}
	with open(CSV_STEAMTABLE) as f:
		reader = DictReader(f)
		for row in reader: steam_pressure[row['Pressure']] = row['hg(j)']
	water_temp ={}
	with open(CSV_WATER_STEAMTABLE) as f:
		reader = DictReader(f)
		for row in reader: water_temp[row['Temp']] = row['hf(j)']
	
	# A : Specific enthalpy of evaporation at atmospheric pressure (hfg)
	A = float(readall_csv2(CSV_STEAMTABLE, ['1'], 'Pressure', 'hfg(j)')[0])	
	app = MainWindow()
	app.mainloop()
