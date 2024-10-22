import pandas as pd
from typing import Callable
from .. import Quantity

Q_ = Quantity

"""ASHRAE Fundamentals 2021, Chapter 18, §18.4
Table 1 Representative Rates at Which Heat and Moisture Are Given Off by Human Beings in Different States of Activity
LowV , HighV is %Sensible Heat that is radiant in any air velocity"""
human_hr_df = pd.DataFrame([
	['Seated, very light work'      ,'Office',   70,  45, 60, 27],
	['Moderately active office work','Office',   75,  55, 58, 38],
	['Light bench work'				,'Factory',  80, 140, 49, 35],
	['Light machine work'			,'Factory', 110, 185, 49, 35],
	['Heavy work'					,'Factory', 170, 255, 54, 19],
	['Heavy machine work; lifting'	,'Factory', 185, 285, 54, 19]],
	columns=['Degree of Activity', 'Location', 'Sensible', 'Latent', 'LowV_F_Rad', 'HighV_F_Rad'])

def HumanHeatRate(activity:str, location:str|None = None) -> tuple[int, int, int, int]:
	if location is not None:
		rowdata = human_hr_df[human_hr_df['Degree of Activity'].str.match(activity) & human_hr_df.Location.str.match(location)]
	else:
		rowdata = human_hr_df[human_hr_df['Degree of Activity'].str.match(activity)]
	return rowdata['Sensible'].values[0], rowdata['Latent'].values[0], rowdata['LowV_F_Rad'].values[0], rowdata['HighV_F_Rad'].values[0]

def SensibleHumanHeatRate(activity:str, location:str) -> int:
	return HumanHeatRate(activity, location)[0]

def LatentHumanHeatRate(activity:str, location:str) -> int:
	return HumanHeatRate(activity, location)[1]

def LowV_F_Rad(activity:str, location:str) -> int:
	return HumanHeatRate(activity, location)[2]

def HighV_F_Rad(activity:str, location:str) -> int:
	return HumanHeatRate(activity, location)[3]

class People:

	def __init__(self):
		self.ID: str = ''
		self.Q_dot_sen_person: Quantity
		self.Q_dot_lat_person: Quantity
		self.F_rad: Quantity
		self.schedule: Callable[[float], float] | None = None
	
	@classmethod
	def create(cls, ID: str,
			   Q_dot_sen_person: Quantity,
			   Q_dot_lat_person: Quantity,
			   F_rad: Quantity,
			   schedule: Callable[[float], float]
	) -> 'People':
		"""Creates a `People` object. (see ASHRAE Fundamentals 2021, Chapter 18, table 1).

		Parameters
		----------
		ID:
			Identifier for the internal heat gain
		Q_dot_sen_person :
			Sensible heat release per person.
		Q_dot_lat_person :
			Latent heat release per person.
		F_rad :
			Fraction of sensible heat release that is radiant.
		schedule :
			Function with signature f(t_sol_sec: float) -> int that takes the
			solar time in seconds from midnight (0 s) and returns the number
			of people in the thermal zone.
		"""
		phg = cls()
		phg.ID = ID
		phg.Q_dot_sen_person = Q_dot_sen_person.to('W')
		phg.Q_dot_lat_person = Q_dot_lat_person.to('W')
		phg.F_rad = F_rad
		phg.schedule = schedule
		return phg

	def calculate_heat_gain(self, t_sol_sec: float) -> tuple[float, float, float, float]:
		Q_dot_sen = self.schedule(t_sol_sec) * self.Q_dot_sen_person.m
		Q_dot_sen_rd = self.F_rad.to('').m * Q_dot_sen
		Q_dot_sen_cv = Q_dot_sen - Q_dot_sen_rd
		Q_dot_lat = self.schedule(t_sol_sec) * self.Q_dot_lat_person.m
		return Q_dot_sen, Q_dot_sen_rd, Q_dot_sen_cv, Q_dot_lat