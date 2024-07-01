import webbrowser
import tkinter as tk
import customtkinter as Ctk
from CTkScrollableDropdown import *
from csv import DictReader
from PIL import Image
from lib.pyCSV import LibFile, readall_csv2
from BoilerRating import BoilerRating
from SteamFlow import SteamFlow
from Deaerator import Deaerator
from BoilerHorsepower import BoilerHorsepower

class SideMenuFrame(Ctk.CTkFrame):
    def __init__(self, master, title, menus, commander):
        super().__init__(master)
        self.variable = Ctk.StringVar(value=menus[0])
        self.title = Ctk.CTkLabel(self, text=title, fg_color="gray30", corner_radius=6, text_color='orange')
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=tk.EW)
        for i, value in enumerate(menus):
            radiobutton = Ctk.CTkRadioButton(self, text=value, value=value, variable=self.variable, command=commander)
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky=tk.W)
        link = Ctk.CTkLabel(self, image=Ctk.CTkImage(light_image=Image.open('images/ie.png'), size=(30, 30)), text='', cursor='hand2')
        link.grid(column=0, row=i + 2, sticky=tk.SE, padx=10, pady=(0, 10))
        link.bind("<Button-1>", lambda e: webbrowser.open(master.url))
        self.rowconfigure(i + 2, weight=1)

    def get(self):
        return self.variable.get()

class MainWindow(Ctk.CTk):
    def ShowMainFrame(self):
        for i in self.menu_frame:
            i.grid_forget()
        menu_index = self.main_menu.index(self.SideMenu_frame.get())
        self.menu_frame[menu_index].grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        self.url = self.url_menu[menu_index]
        self.geometry(self.window_menu[menu_index])

    def Theme(self, e):
        if self.mode == "dark":
            Ctk.set_appearance_mode("light")
            self.mode = "light"
        else:
            Ctk.set_appearance_mode("dark")
            self.mode = "dark"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Steam Engineering Toolbox')
        self.iconbitmap('images/logo.ico')
        self.grid_columnconfigure(1, weight=1)
        self.resizable(False, True)

        self.mode = 'dark'
        self.main_menu = ["Boiler Rating", "Steam Flow", "Deaerator", "แรงม้าเสียภาษี"]
        self.url_menu = [
            "https://www.spiraxsarco.com/learn-about-steam/the-boiler-house/boiler-ratings?sc_lang=en-GB",
            "https://www.spiraxsarco.com/learn-about-steam/steam-distribution/pipes-and-pipe-sizing?sc_lang=en-GB",
            "https://www.spiraxsarco.com/learn-about-steam/the-boiler-house/pressurised-deaerators?sc_lang=en-GB",
            "http://industrial.hidofree.com/machine-tools-machinery/boilers-steam-หม้อไอน้ำ/ความหมายของ-bhp-หรือ-แรงม้า/"
        ]
        self.window_menu = ["510x225", "500x318", "510x225", "430x225"]
        self.geometry(self.window_menu[0])
        self.url = self.url_menu[0]
        self.SideMenu_frame = SideMenuFrame(self, title="Main Menu", menus=self.main_menu, commander=self.ShowMainFrame)
        self.SideMenu_frame.grid(row=0, column=0, padx=(3, 0), pady=3, sticky=tk.NSEW)
        self.SideMenu_frame.bind('<Double-Button-1>', self.Theme)

        self.menu_frame = []
        self.BoilerRating_frame = BoilerRating(self, steam_hg, water_temp, A)
        self.menu_frame.append(self.BoilerRating_frame)
        self.SteamFlow_frame = SteamFlow(self, NPS, CSV_PIPETABLE, ODList, THKList, steam_vg)
        self.menu_frame.append(self.SteamFlow_frame)
        self.Deaerator_frame = Deaerator(self, steam_hg, water_temp, A)
        self.menu_frame.append(self.Deaerator_frame)
        self.BoilerHorsepower_frame = BoilerHorsepower(self)
        self.menu_frame.append(self.BoilerHorsepower_frame)
        self.BoilerRating_frame.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)

if __name__ == "__main__":
    NPS = ('15 mm', '20 mm', '25 mm', '32 mm', '40 mm', '50 mm', '65 mm', '80 mm', '100 mm', '125 mm', '150 mm', '200 mm', '250 mm', '300 mm')
    CSV_STEAMTABLE = LibFile('SteamTable.csv')
    CSV_WATER_STEAMTABLE = LibFile('WaterTable.csv')
    CSV_PIPETABLE = LibFile('PipeThickness.csv')
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
    A = float(readall_csv2(CSV_STEAMTABLE, ['0'], 'Pressure', 'hfg(j)')[0])

    app = MainWindow()
    app.mainloop()
