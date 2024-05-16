import os
import tkinter as tk
from tkinter import ttk
from math import pi, sqrt
from csv import DictReader
from pyCSV import ExtensionPath, readall_csv2
# from ctypes import windll
# windll.shcore.SetProcessDpiAwareness(1)

class SteamFlow():
	def NPS_changed(self, e):
		OD = float(ODList[self.cmbNPS.current()])
		thk = float(THKList[self.cmbNPS.current()])
		self.InsideDiameter = (OD - 2*thk)/1000
		self.btnNPS['text'] = 'id {:.3f}'.format(self.InsideDiameter)
	def NPS_click(self):
		F = self.tbFlow.get()
		V = self.tbVelocity.get()
		Vg = float(steam_pressure[self.cmbPressure.get()])
		D = round(sqrt((F*Vg*4)/(3600*pi*V)), 5)
		for i in range(len(NPS)):
			OD = float(ODList[i])
			thk = float(THKList[i])
			if ((OD - 2*thk)/1000) >= D:
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
		SteamVelocity = (F*Vg*4)/(3600*pi*(D*D))
		self.tbVelocity.set(round(SteamVelocity, 2))
	def SteamFlowrate_click(self):
		V = self.tbVelocity.get()
		D = self.InsideDiameter
		Vg = float(steam_pressure[self.cmbPressure.get()])
		SteamFlowrate = (V*3600*pi*(D*D))/(Vg*4)
		self.tbFlow.set(round(SteamFlowrate, 2))
		
	def __init__(self, root):
		self.InsideDiameter = 0.05248
		self.tbVelocity = tk.DoubleVar()
		self.tbVelocity.set(25.0)
		self.tbFlow = tk.DoubleVar()
		self.tbFlow.set(520.53)
		
		tk.Label(root, text='Pipe Size (NPS)').grid(column=0, row=0, sticky=tk.E, padx=5, pady=3)
		self.cmbNPS = ttk.Combobox(root, values=NPS, width=12, justify='right')
		self.cmbNPS.grid(column=1, row=0, sticky=tk.W, padx=5, pady=3)
		self.cmbNPS.bind("<<ComboboxSelected>>", self.NPS_changed)
		self.cmbNPS.set('50 mm') 
		self.btnNPS = tk.Button(root, text='id 0.052', width=10, command=self.NPS_click)
		self.btnNPS.grid(column=3, sticky=tk.W, row=0, padx=5, pady=3)
	   
		tk.Label(root, text='Pipe Schedule').grid(column=0, row=1, sticky=tk.E, padx=5, pady=3)
		self.cmbPS = ttk.Combobox(root, values=['40','80'], width=12, justify='right')		
		self.cmbPS.grid(column=1, row=1, sticky=tk.W, padx=5, pady=3)
		self.cmbPS.bind("<<ComboboxSelected>>", self.PS_changed)
		self.cmbPS.current(0)		

		tk.Label(root, text='Steam Pressure').grid(column=0, row=2, sticky=tk.E, padx=5, pady=3)
		self.cmbPressure = ttk.Combobox(root, width=12, justify='right')
		self.cmbPressure.grid(column=1, row=2, sticky=tk.W, padx=5, pady=3)
		self.cmbPressure['values'] = list(steam_pressure.keys())[1:]
		self.cmbPressure.set('4')
		tk.Label(root, text='bar.g').grid(column=2, row=2, sticky=tk.W)
	   
		tk.Label(root, text='Velocity').grid(column=0, row=3, sticky=tk.E, padx=5, pady=3)
		tk.Entry(root, textvariable=self.tbVelocity, width=15, justify='right').grid(column=1, row=3, sticky=tk.W, padx=5, pady=3)
		tk.Label(root, text='m/s').grid(column=2, row=3, sticky=tk.W)
		tk.Button(root, text='Velocity', width=10, command=self.SteamVelocity_click).grid(column=3, sticky=tk.W, row=3, padx=5, pady=3)
	   
		tk.Label(root, text='Flow').grid(column=0, row=4, sticky=tk.E, padx=5, pady=3)
		tk.Entry(root, textvariable=self.tbFlow, width=15, justify='right').grid(column=1, row=4, sticky=tk.W, padx=5, pady=3)
		tk.Label(root, text='kg/hr').grid(column=2, row=4, sticky=tk.W)
		tk.Button(root, text='Flowrate', width=10, command=self.SteamFlowrate_click).grid(column=3, sticky=tk.W, row=4, padx=5, pady=3)
	   
		ttk.Separator(root, orient='horizontal').grid(column=0, columnspan=4, row=5, sticky='ew', padx=10, pady=3)
		
		# home_icon = tk.PhotoImage(file=os.path.join(scriptpath, 'images/Formula.png'))	
		home_icon = tk.PhotoImage(file='images/Formula.png')
		canvas = tk.Label(root, image=home_icon)
		canvas.grid(column=0, columnspan=4, row=6, sticky='ew')
		canvas.image = home_icon
		
NPS = ('15 mm','20 mm','25 mm','32 mm','40 mm','50 mm','65 mm','80 mm','100 mm','125 mm','150 mm','200 mm','250 mm','300 mm')
CSV_PIPETABLE = os.path.normpath(os.path.join(ExtensionPath(), 'PipeThickness.csv'))
CSV_STEAMTABLE = os.path.normpath(os.path.join(ExtensionPath(), 'SteamTable.csv'))
ODList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', 'OD')
THKList = readall_csv2(CSV_PIPETABLE, NPS, 'nps', '40')
steam_pressure = {}
with open(CSV_STEAMTABLE) as f:
	reader = DictReader(f)
	for row in reader:
		steam_pressure[row['Pressure']] = row['Vg']

if __name__ == "__main__":
#    scriptpath  = os.path.dirname(os.path.abspath(__file__))
   root = tk.Tk()
   root.geometry("350x255")
   root.title('Steam Flow')
   root.resizable(0, 0)    #don't allow resize in x or y direction
   
   root.columnconfigure(0, weight=8)
   root.columnconfigure(1, weight=5)
   root.columnconfigure(2, weight=1)
   root.columnconfigure(3, weight=4)

   app = SteamFlow(root)
   root.mainloop()