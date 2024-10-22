from __future__ import annotations
import pandas as pd
from datetime import date as Date
from .. import Quantity
from .time import *
from .geometry import *
from .radiation import ClimateType, ext_irradiance_normal, equation_of_time

Q_ = Quantity

# from ASHRAE Handbook-Fundamentals 2021 p14.13
# Table 6 Fraction of Daily Temperature Range
daily_temp_rng_fractions = [	
	0.88, 0.92, 0.95, 0.98, 1.00, 0.98, 0.91, 0.74, 0.55, 0.38, 0.23, 0.13, 
	0.05, 0.00, 0.00, 0.06, 0.14, 0.24, 0.39, 0.50, 0.59, 0.68, 0.75, 0.82 ]
# daily_temp_rng_fractions = [	
# 	0.92, 0.95, 0.98, 1.00, 0.98, 0.91, 0.74, 0.55, 0.38, 0.23, 0.13, 
# 	0.05, 0.00, 0.00, 0.06, 0.14, 0.24, 0.39, 0.50, 0.59, 0.68, 0.75, 0.82, 0.88 ]


class ReferenceDates:
	_dates: dict[str, Date] = {
		'jan': Date(2024,  1, 17),
		'feb': Date(2024,  2, 16),
		'mar': Date(2024,  3, 16),
		'apr': Date(2024,  4, 15),
		'may': Date(2024,  5, 15),
		'jun': Date(2024,  6, 11),
		'jul': Date(2024,  7, 17),
		'aug': Date(2024,  8, 16),
		'sep': Date(2024,  9, 15),
		'oct': Date(2024, 10, 15),
		'nov': Date(2024, 11, 14),
		'dec': Date(2024, 12, 10)}
	# _dates: dict[str, Date] = {
	# 	'jan': Date(2024,  1, 21),
	# 	'feb': Date(2024,  2, 21),
	# 	'mar': Date(2024,  3, 21),
	# 	'apr': Date(2024,  4, 21),
	# 	'may': Date(2024,  5, 21),
	# 	'jun': Date(2024,  6, 21),
	# 	'jul': Date(2024,  7, 21),
	# 	'aug': Date(2024,  8, 21),
	# 	'sep': Date(2024,  9, 21),
	# 	'oct': Date(2024, 10, 21),
	# 	'nov': Date(2024, 11, 21),
	# 	'dec': Date(2024, 12, 21)}

	@classmethod
	def get_date_for(cls, m: str | int) -> Date:
		if isinstance(m, int) and 1 <= m <= 12:
			month = list(cls._dates.keys())[m - 1]
		elif isinstance(m, str):
			for month in cls._dates.keys():
				if month in m.lower():
					month = month
					break
			else:
				raise ValueError(f'month {m} does not exist')
		else:
			raise ValueError(f'month {m} does not exist')
		return cls._dates[month]

	@classmethod
	def months(cls):
		for m in cls._dates.keys():
			yield m

class WeatherData:
	"""Contains the routines to create the hourly outdoor temperature profiles (dry-bulb and wet-bulb)
	T_db_prof -> Column 3 'Outdoor Temp.' Table 29B ASHRAE Handbook-Fundamentals 2021 p18.50
	"""
	def __init__(self) -> None:
		self.ID : str
		self._fi: Quantity | None = None
		self._L_loc: Quantity | None = None
		self._altitude : Quantity | None = None
		self._date: Date = Date(2024, 4, 21)
		self._T_db_des : Quantity | None = None
		self._T_db_rng : Quantity | None = None
		self._T_wb_mc: Quantity | None = None
		self._T_wb_rng: Quantity | None = None
		self.T_db_prof: list[Quantity] | None = None
		self.T_wb_prof: list[Quantity] | None = None
		# self.T_db_max: Quantity | None = None
		# self.T_db_avg: Quantity | None = None
		self._taub: float = 0
		self._taud: float = 0
		self._tz: int = 7
		self._timezone: str = 'Asia/Bangkok'
		self._climate_type: str = ClimateType.TROPICAL
		self.position_df: pd.DataFrame | None = None

	@classmethod
	def create_from_climatic_design_data(cls, ID: str,
										 fi: Quantity, 
										 L_loc: Quantity,		
										 altitude: Quantity,		
										 date: Date,		
										 T_db_des: Quantity,		
										 T_db_rng: Quantity,		
										 T_wb_mc: Quantity,		
										 T_wb_rng: Quantity,		
										 taub : float,		
										 taud : float,		
										 tz: int = 7,		
										 timezone: str = 'Asia/Bangkok',		
										 climate_type: str = ClimateType.TROPICAL) -> WeatherData:
		"""Creates `WeatherData` object from climatic design information that
		can be looked up in e.g. ASHRAE's data tables. 

		Parameters
		----------
		fi:
			Latitude of the location; north positive; -pi/2 <= fi <= pi/2
		L_loc:
			Longitude of the location; positive east of Greenwich, negative west of Greenwich.
			Bangkok 100.564E L_loc=100.56, Atlanta GA L_loc=-84.442W
		date: Date, optional
			Current date at the location.
		altitude: Quantity, optional
			Altitude of the location.        
		date:
			Date for which the weather data is valid.
		T_db_des:
			Monthly design dry-bulb temperature, i.e., the maximum temperature
			on the selected day.
		T_db_rng:
			Mean daily temperature range, i.e., the difference between the
			maximum and the minimum temperature on the selected day.
		T_wb_mc:
			Mean coincident wet-bulb temperature.
		T_wb_rng:
			Mean coincident daily wet-bulb temperature range.
		tz : optional, time zone of the location, expressed in hours ahead or
			behind coordinated universal time (UTC) UTC:+7 for THAILAND
		timezone: optional, default UTC
			Tz-database identifier of the time zone of the location, indicating
			the offset from UTC (e.g. Etc/GMT-1).
			See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
			The time zone is only used to determine the local standard time
			meridian. Do not specify a timezone with daylight saving time (DST),
			should it be in use at the location under consideration, as this may
			give errors at times when DST becomes active or inactive (e.g. use
			'Etc/GMT-1' instead of 'Europe/Brussels').
		climate_type:
			Type of climate as defined in class `ClimateType`

		References
		----------
		ASHRAE Handbook-Fundamentals 2021, Chapter 14 Climatic Design Information."""
		obj = cls()
		obj.ID = ID
		obj._fi = fi.to('rad')  # `.to(...)` returns new object
		obj._L_loc = L_loc
		obj._altitude = altitude		
		obj._date = date
		obj._T_db_des = T_db_des
		obj._T_db_rng = T_db_rng
		obj._T_wb_mc = T_wb_mc 
		obj._T_wb_rng = T_wb_rng		
		obj._taub = taub
		obj._taud = taud
		obj._tz = tz
		obj._timezone = timezone
		obj._climate_type = climate_type
		obj.synthetic_daily_db_profiles()
		obj.synthetic_daily_wb_profiles()
		return obj

	# property & Setter
	# region
	@property
	def fi(self) -> Quantity:
		"""Latitude of the location."""
		return self._fi
	@fi.setter
	def fi(self, v: Quantity) -> None:
		"""Set latitude of the location."""
		self._fi = v.to('rad')
		# ensure that `fi` is always in radians

	@property
	def L_loc(self) -> Quantity:
		"""Longitude of the location."""
		return self._L_loc
	@L_loc.setter
	def L_loc(self, v: Quantity) -> None:
		"""Set longitude of the location."""
		self._L_loc = v
		
	@property
	def altitude(self) -> Quantity:
		"""Altitude of location."""
		return self._altitude
	@altitude.setter
	def altitude(self, v: Quantity) -> None:
		"""Set altitude of location."""
		self._altitude = v
		
	@property
	def date(self) -> Date:
		"""Current date at the location."""
		return self._date
	@date.setter
	def date(self, date: Date):
		"""Set the current date at the location."""
		self._date = date

	@property
	def T_db_des(self) -> Quantity:
		return self._T_db_des
	@T_db_des.setter
	def T_db_des(self, v: Quantity):
		self._T_db_des = v

	@property
	def T_db_rng(self) -> Quantity:
		return self._T_db_rng
	@T_db_rng.setter
	def T_db_rng(self, v: Quantity):
		self._T_db_rng = v

	@property
	def T_wb_mc(self) -> Quantity:
		return self._T_wb_mc
	@T_wb_mc.setter
	def T_wb_mc(self, v: Quantity):
		self._T_wb_mc = v

	@property
	def T_wb_rng(self) -> Quantity:
		return self._T_wb_rng
	@T_wb_rng.setter
	def T_wb_rng(self, v: Quantity):
		self._T_wb_rng = v

	@property
	def tz(self) -> int:
		return self._tz
	@tz.setter
	def tz(self, v: int) -> None:
		self._tz = v	
	
	@property
	def timezone(self) -> str:
		"""Timezone of the location."""
		return self._timezone
	@timezone.setter
	def timezone(self, v: str) -> None:
		"""Set timezone of the location."""
		self._timezone = v

	@property
	def taub(self) -> float:
		return self._taub
	@taub.setter
	def taub(self, v: float) -> None:
		self._taub = v

	@property
	def taud(self) -> float:
		return self._taud
	@taud.setter
	def taud(self, v: float) -> None:
		self._taud = v

	@property
	def T_db_max(self) -> Quantity:
		return max(self.T_db_prof)

	@property
	def T_db_avg(self) -> Quantity:
		return sum(T_db.to('K') for T_db in self.T_db_prof) / len(self.T_db_prof)

	@property
	def declination(self) -> Quantity:
		return Q_(declination(day_number(self._date)), 'rad')	

	@property
	def E0(self) -> float:
		"""extraterrestrial normal irradiance"""
		dates = day_number(self.date)
		return ext_irradiance_normal(dates)

	@property
	def Et(self) -> float:
		"""equation of time"""
		dates = day_number(self.date)
		return equation_of_time(dates)
	# endregion

	def synthetic_daily_db_profiles(self):
		""" Creates Outside Air Temperatures for each hour (0..23 h) calculated 
		according to ASHRAE Handbook-Fundamentals 2021 p14.12, Temperatures."""
		self.T_db_prof = [dry_bulb_temperature(t_sol_dec, self.T_db_des, self.T_db_rng) for t_sol_dec in range(0, 24)]
	
	def synthetic_daily_wb_profiles(self):
		""" Creates Outside Air Temperatures for each hour (0..23 h) calculated 
		according to ASHRAE Handbook-Fundamentals 2021 p14.12, Temperatures."""
		self.T_wb_prof = [wet_bulb_temperature(t_sol_dec, self.T_wb_mc, self.T_wb_rng) for t_sol_dec in range(0, 24)]

	def update_sun_position(self, lst: float | np.ndarray = np.array([i for i in range(24)])) -> pd.DataFrame:
		"""Update Sun Position (AST, Hour Angle, Altitude, Aziuth, Air Mass etc. of the sun).
		ASHRAE Handbook-Fundamentals 2021 p14.10
		All expressed in degrees
		"""
		df = pd.DataFrame(lst, columns=['LST'])
		dates = day_number(self.date)

		# AST : Apparent Solar Ttime
		AST = apparent_solar_time(LST=lst, n=dates, LON=self.L_loc, TZ=self.tz)
		df['AST'] = AST

		# Hour Angle
		H = hour_angle(AST, rad_unit=False)
		df['H'] = H

		# Solar Altitude
		_declination = self.declination.m
		fi = self.fi.m
		beta = np.arcsin(np.cos(fi)*np.cos(_declination)*np.cos(np.deg2rad(H)) + np.sin(fi)*np.sin(_declination))
		df['Altitude'] = np.rad2deg(beta)

		# ASHRAE Fundamentals 2021 p18.48
		# Solar azimuth. By convention, it is counted positive for afternoon hours and negative for morning hours.
		afternoon = AST.copy()
		afternoon[afternoon < 12] = -1
		afternoon[afternoon != -1] = 1
		phi = np.arccos((np.sin(beta)*np.sin(fi) - np.sin(_declination))/(np.cos(beta)*np.cos(fi)))
		phi = phi * afternoon
		df['Azimuth'] = np.rad2deg(phi)

		# ASHRAE Fundamentals 2021 p14.10 Air Mass
		beta_degree = df['Altitude'].tolist()
		beta_degree = np.array([0 if x < 0 else x for x in beta_degree])		
		m = 1/(np.sin(beta) + 0.50572*(6.07995 + beta_degree) ** -1.6364)
		m[m < 0] = 0
		df['AirMaass'] = m

		# E0 = extraterrestrial normal irradiance
		# Eb = beam normal irradiance (measured perpendicularly to rays of the sun)
		# Ed = diffuse horizontal irradiance (measured on horizontal surface)
		ab = 1.454 - 0.406*self.taub - 0.268*self.taud + 0.021*self.taub*self.taud
		ad = 0.507 + 0.205*self.taub - 0.080*self.taud - 0.190*self.taub*self.taud

		E0 = ext_irradiance_normal(dates)
		Eb = E0 * np.exp(-self.taub * (m ** ab))
		Eb[Eb == E0] = 0
		Ed = E0 * np.exp(-self.taud * (m ** ad))
		Ed[Ed == E0] = 0
		df['Eb(W/m2)'] = Eb
		df['Ed(W/m2)'] = Ed
		self.position_df = df
		return df

def dry_bulb_temperature(t_sol_dec: float, T_db_des: Quantity, T_db_rng: Quantity) -> Quantity:
	"""Returns the dry-bulb temperature at `t_sol_dec`, calculated according to
	ASHRAE Handbook-Fundamentals 2021 p14.12, Temperatures.

	Parameters
	----------
	t_sol_dec:
		Solar time in decimal hours.
	T_db_des:
		Dry-bulb design temperature.
	T_db_rng:
		Mean coincident daily dry-bulb temperature range.
	"""
	T_db_des = T_db_des.to('degC').magnitude
	T_db_rng = T_db_rng.to('delta_degC').magnitude
	t_sol_hr = int(round(t_sol_dec))
	frac = daily_temp_rng_fractions[t_sol_hr]
	T_db = T_db_des - frac * T_db_rng
	return Q_(T_db, 'degC')

def wet_bulb_temperature(t_sol_dec: float, T_wb_mc: Quantity, T_wb_rng: Quantity) -> Quantity:
	"""Returns the wet-bulb temperature at `t_sol_dec`, calculated according to
	ASHRAE Handbook-Fundamentals 2021 p14.12, Temperatures.

	Parameters
	----------
	t_sol_dec:
		Solar time in decimal hours.
	T_wb_mc:
		The mean coincident wet-bulb temperature that goes with `T_db_des`.
	T_wb_rng:
		Mean coincident daily wet-bulb temperature range.
	"""
	T_wb_mc = T_wb_mc.to('degC').magnitude
	T_wb_rng = T_wb_rng.to('delta_degC').magnitude
	t_sol_hr = int(round(t_sol_dec))
	frac = daily_temp_rng_fractions[t_sol_hr]
	T_wb = T_wb_mc - frac * T_wb_rng
	return Q_(T_wb, 'degC')
