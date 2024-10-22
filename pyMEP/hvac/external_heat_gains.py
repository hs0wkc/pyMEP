from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from enum import Enum
from .. import Quantity
from .climatic import WeatherData
from .coolingload import Setting, TimeSeriesMethod

Q_ = Quantity

class Building_Element(ABC):
	weather_data: WeatherData
	net_area: Quantity
	U : Quantity
	sigma : Quantity													# ASHRAE Fundamentals 2021 p14.11 tilt angle
	NS_RTS : pd.DataFrame
	solar_irradiance_df : pd.DataFrame | None = None	
	cooling_load_df : pd.DataFrame | None = None	

	def __init__(self, id: str) -> None:
		self.ID = id
		self.psi = Q_(0, 'deg')											# ASHRAE Fundamentals 2021 p14.11 surface azimuth		
		self.surface_absorptance : float = Setting.surface_absorptance	# ASHRAE Fundamentals 2021 p18.25 Surface Absorptance
		self.delta_T = Setting.delta_T
		self.CTS = [12,43,26,11,5,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]		
	
	@abstractmethod
	def update_cooling_load(self) -> pd.DataFrame:
		"""Update Cooling Load Component DataFrame as current component.
		"""
		...

	def Update_ns_rts(self, ns_rts: pd.DataFrame) -> None:
		self.NS_RTS = ns_rts
		self.update_cooling_load()
	
class Roof(Building_Element):
	def __init__(self, id: str) -> None:
		super().__init__(id=id)
		self.F_rad = Setting.Roof_F_rad
		self.sigma = Q_(0, 'deg')		

	def update_cooling_load(self) -> pd.DataFrame:
		"""ASHRAE Fundamentals 2021 p14.11
		Calculation of Clear-Sky Solar Irradiance Incident On Receiving Surface"""
		self.solar_irradiance_df = _solar_irradiance(element=self)

		"""ASHRAE Fundamentals 2021 p18.24
		Heat Gain Through Exterior Surface"""
		self.cooling_load_df = self.solar_irradiance_df[['LST','Et(W/m2)']].copy()
		_external_cooling_load(element=self, long_wave_correction=Setting.hlwc)
		return self.cooling_load_df

class Ceiling(Building_Element):
	def __init__(self, id: str) -> None:
		super().__init__(id=id)

	def update_cooling_load(self) -> pd.DataFrame:
		self.cooling_load_df = self.weather_data.position_df[['LST']].copy()
		_internal_cooling_load(element=self)
		return self.cooling_load_df

class Floor(Building_Element):
	def __init__(self, id: str) -> None:
		super().__init__(id=id)
	
	def update_cooling_load(self) -> pd.DataFrame:
		self.cooling_load_df = self.weather_data.position_df[['LST']].copy()
		_internal_cooling_load(element=self)
		return self.cooling_load_df

class Wall(Building_Element):
	
	class WallType(Enum):
		External = True
		Internal = False	
	
	def __init__(self, id: str) -> None:
		super().__init__(id=id)
		self.F_rad = Setting.Wall_F_rad
		self.sigma = Q_(90, 'deg')
		self.wall_type = self.WallType.External
		self.windows: dict[str, Window] = {}

	@classmethod
	def creat_external_wall(cls, id: str,
							weather_data: WeatherData,							
							gross_area : Quantity,
							U: Quantity,
							NS_RTS: pd.DataFrame,
							CTS: list,
							surface_azimuth: Quantity,							
							tilt_angle: Quantity = Q_(90, 'deg'),							
							surface_absorptance : float = Setting.surface_absorptance							
							) -> Building_Element:
		obj = cls(id=id)
		obj.weather_data = weather_data
		obj.wall_type = cls.WallType.External
		obj.net_area = gross_area
		obj.U = U
		obj.NS_RTS = NS_RTS
		obj.CTS = CTS
		obj.psi = surface_azimuth
		obj.sigma = tilt_angle.to('rad')
		obj.surface_absorptance = surface_absorptance		
		return obj

	@classmethod
	def creat_internal_wall(cls, id: str,
							weather_data: WeatherData,
							gross_area: Quantity,
							U: Quantity,
							NS_RTS: pd.DataFrame,
							delta_T: Quantity = Setting.delta_T
							) -> Building_Element:
		obj = cls(id=id)
		obj.weather_data = weather_data
		obj.wall_type = cls.WallType.Internal
		obj.net_area = gross_area
		obj.U = U
		obj.NS_RTS = NS_RTS
		obj.delta_T = delta_T
		return obj

	def add_window(self, id: str, width: Quantity, height: Quantity, U: Quantity, SC:float) -> Building_Element:
		window = Window.creat(id=id, host=self, width=width, height=height, U=U, SC=SC)
		self.windows[window.ID] = window
		self.net_area -= window.net_area
		return window

	def remove_window(self, ID: str):
		self.windows.pop(ID)

	def clear_window(self):
		self.windows.clear()

	def update_cooling_load(self) -> pd.DataFrame:
		if self.wall_type == self.WallType.External:
			"""ASHRAE Fundamentals 2021 p14.11
			Calculation of Clear-Sky Solar Irradiance Incident On Receiving Surface"""
			self.solar_irradiance_df = _solar_irradiance(element=self)

			"""ASHRAE Fundamentals 2021 p18.24
			Heat Gain Through Exterior Surface"""
			self.cooling_load_df = self.solar_irradiance_df[['LST','Et(W/m2)']].copy()
			_external_cooling_load(element=self, long_wave_correction=Setting.vlwc)
		else:
			self.cooling_load_df = self.weather_data.position_df[['LST']].copy()
			_internal_cooling_load(element=self)
		return self.cooling_load_df

class Window(Building_Element):

	window_SHG_df : pd.DataFrame

	def __init__(self, id: str):
		super().__init__(id=id)
		self._width : Quantity = Q_(0, 'm')
		self._height : Quantity = Q_(0, 'm')
		self.host : Wall
		self.SC : float
		self.SHGCd : list[float]
		self.SHGCh : float
		self.S_RTS : pd.DataFrame

	@classmethod
	def creat(cls, id: str,
			  host: Wall,
			  width: Quantity,
			  height: Quantity,
			  U: Quantity,
			  SC : float
			  ) -> Building_Element:
		obj = cls(id=id)
		obj.host = host
		obj.weather_data = host.weather_data
		obj.psi = host.psi
		obj.Width = width
		obj.Height = height
		obj.U = U
		obj.SC = SC
		return obj

	def update_cooling_load(self) -> pd.DataFrame:
		df = self.host.solar_irradiance_df[['LST','Etb(W/m2)','Etd(W/m2)','Etr(W/m2)','Incidence']].copy()
		Incidence = df['Incidence'].to_numpy()
		Incidence[Incidence > 90] = 0
		x = np.array([0, 40, 50, 60, 70, 80, 90])
		y = np.array(self.SHGCd)
		fx = interp1d(x, y)
		SHGC = fx(Incidence)
		df['SHGC'] = SHGC

		# Direct Solar Heat Gain
		Etb = df['Etb(W/m2)'].to_numpy()
		qb = self.net_area*Etb*SHGC*self.SC
		df['qbHG'] = qb

		# Diffuse Solar Heat Gain
		Etd = df['Etd(W/m2)'].to_numpy()
		Etr = df['Etr(W/m2)'].to_numpy()
		qd = self.net_area*(Etd+Etr)*self.SHGCh
		df['qdHG'] = qd

		# Conduction Heat Gain
		Tout = self.host.cooling_load_df['Out_T'].to_numpy()
		df['Out_T'] = Tout
		cdhg = self.U*self.net_area*(Tout - Setting.Inside_DB.m)
		df['CondHG'] = cdhg

		# Total Window Heat Gain
		TOTAL_HG = qb+qd+cdhg
		df['TOTAL_HG'] = TOTAL_HG
		self.window_SHG_df = df

		df = self.window_SHG_df[['LST','qbHG']].copy()

		# S-RTS
		s_rts = self.S_RTS['S-RTS'].tolist()
		df['S-RTS'] = s_rts

		# Direct Solar Cooling Load
		di_CL = TimeSeriesMethod(ts=s_rts, heat_load=qb.m.tolist(), id=self.ID, tstype='S-RTS')
		df['di_CL'] = di_CL

		# Heat Gain
		df[['qdHG','CondHG']] = self.window_SHG_df[['qdHG','CondHG']]
		hg = qd+cdhg
		df['Heat Gain'] = hg

		# Convective Heat Gain
		F_rad = SHGC
		F_rad[F_rad > 0.5] = Setting.Window_hshgc_F_rad
		F_rad[F_rad != Setting.Window_hshgc_F_rad] = Setting.Window_lshgc_F_rad
		cvhg = (1-F_rad)*hg
		df['ConvHG'] = cvhg
		
		# Radiant Heat Gain
		rhg = hg - cvhg
		df['RadHG'] = rhg

		# NS-RTS
		ns_rts = self.host.NS_RTS['NS-RTS'].tolist()
		df['NS-RTS'] = ns_rts

		# RTS_CL
		rts_cl = TimeSeriesMethod(ts=ns_rts, heat_load=rhg.m.tolist(), id=self.ID, tstype='NS-RTS')
		df['RTS_CL'] = rts_cl

		# Total Cooling Load
		total_cl = di_CL + cvhg.m + rts_cl
		df['TOTAL_CL'] = total_cl

		self.cooling_load_df = df		
		return df

	@property
	def Width(self) -> Quantity:
		return self._width
	@Width.setter
	def Width(self, v: Quantity) -> None:
		self._width = v
		self.net_area = self._width * self._height

	@property
	def Height(self) -> Quantity:
		return self._height
	@Height.setter
	def Height(self, v: Quantity) -> None:
		self._height = v
		self.net_area = self._width * self._height

def _solar_irradiance(element : Building_Element)-> pd.DataFrame:
	"""ASHRAE Fundamentals 2021, p14.11
	Solar Angles Related to Receiving Surfaces
	The tilt angle Σ(sigma) (also called slope) is the angle between the surface and the horizontal
	plane. Its value lies between 0 and 180°. Most often, slopes are between 0° (horizontal) and 
	90° (vertical). Values above 90° correspond to surfaces facing the ground.
	The surface azimuth Ψ(psi) is defined as the displacement from south of the projection, 
	on the horizontal plane, of the normal to the surface. Surfaces that face west have a 
	positive surface azimuth; those that face east have a negativesurface azimuth. 
	Note that, surface azimuth is defined as relative to south in both the northern and southern
	hemispheres.
	"""
	df = element.weather_data.position_df[['LST','Eb(W/m2)','Ed(W/m2)']].copy()	

	"""The surface-solar azimuth angle γ(gamma) is defined as the angular difference between
	the solar azimuth Φ(phi) and the surface azimuth Ψ(psi)
	Values of γ(gamma) greater than 90° or less than –90° indicate that the surface is in the shade."""	
	gamma = element.weather_data.position_df['Azimuth'].to_numpy() - element.psi.m
	sigma = element.sigma.m
	df['γ-gamma'] = gamma
	
	# Surface Incidence
	beta = element.weather_data.position_df['Altitude'].to_numpy()
	theta = np.arccos(np.cos(np.deg2rad(beta))*np.cos(np.deg2rad(gamma))*np.sin(np.deg2rad(sigma)) 
			+ np.sin(np.deg2rad(beta))*np.cos(np.deg2rad(sigma)))
	df['Incidence'] = np.rad2deg(theta)
	
	# Direct Beam solar
	Eb = df['Eb(W/m2)'].to_numpy()
	Etb = Eb*np.cos(theta)
	Etb[Etb <= 0] = 0
	df['Etb(W/m2)'] = Etb
	
	# Diffuse Solar HeatGain
	Y = 0.55 + 0.437*np.cos(theta) + 0.313*(np.cos(theta)**2)
	Y[Y < 0.45] = 0.45
	df['Y'] = Y
	Ed = df['Ed(W/m2)'].to_numpy()
	Etd = Ed*(Y*np.sin(np.deg2rad(sigma)) + np.cos(np.deg2rad(sigma))) if sigma <= 90 else Ed*Y*np.sin(np.deg2rad(sigma))
	df['Etd(W/m2)'] = Etd
	
	# Ground Diffuse
	# ρ (rho) : Ground Reflectance of Foreground Surfaces
	Etr = (Eb*np.sin(np.deg2rad(beta)) + Ed) * Setting.rho * (1-np.cos(np.deg2rad(sigma)))/2
	df['Etr(W/m2)'] = Etr

	# Total Surface Irradiance
	Et = Etb + Etd + Etr
	df['Et(W/m2)'] = Et
	# df.set_index('LST', inplace=True, drop=False)
	return df

def _external_cooling_load(element : Building_Element, long_wave_correction : float) -> pd.DataFrame:
	df = element.cooling_load_df

	# Outdoor Temperature from Weather data
	Tout = np.array([i.m for i in element.weather_data.T_db_prof])
	df['Out_T'] = Tout

	# Sol-air temperature
	Et = df['Et(W/m2)'].to_numpy()
	Te = Tout + element.surface_absorptance * Et - long_wave_correction
	df['Sol-Air_T'] = Te

	# Heat Input
	qi = element.U * element.net_area * (Te - Setting.Inside_DB.m)
	df['Heat Input'] = qi.m

	# Conduction Time Series
	df['CTS'] = element.CTS

	# Heat Gain
	hg = TimeSeriesMethod(ts=element.CTS, heat_load=qi.m.tolist(), id=element.ID , tstype='CTS')
	df['Heat Gain'] = hg

	# Convective Heat Gain
	cvhg = (1-element.F_rad)*hg
	df['ConvHG'] = cvhg

	# Radiant Heat Gain
	rhg = element.F_rad*hg
	df['RadHG'] = rhg

	# NS-RTS
	ns_rts=element.NS_RTS['NS-RTS'].tolist()
	df['NS-RTS'] = ns_rts

	# RTS_CL
	rts_cl = TimeSeriesMethod(ts=ns_rts, heat_load=rhg.tolist(), id=element.ID, tstype='NS-RTS')
	df['RTS_CL'] = rts_cl

	# Total Cooling Load
	total_cl = cvhg + rts_cl
	df['TOTAL_CL'] = total_cl
	
	return df

def _internal_cooling_load(element : Building_Element) -> pd.DataFrame:
	df = element.cooling_load_df

	# Outdoor Temperature from Temperature Diff. with adjacent space
	Tout = Setting.Inside_DB + element.delta_T
	df['Out_T'] = Tout.magnitude

	# Indoor temperature
	df['In_T'] = Setting.Inside_DB.m

	# Total Cooling Load
	Te=df['Out_T'].to_numpy()
	qi = element.U * element.net_area * (Te - Setting.Inside_DB.m)
	df['TOTAL_CL'] = qi.m

	return df