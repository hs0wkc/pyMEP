from psychrolib import SetUnitSystem, SI, CalcPsychrometricsFromTWetBulb, CalcPsychrometricsFromRelHum
from pyMEP import Quantity
from pyMEP.hvac.climatic import WeatherData, ReferenceDates
from pyMEP.hvac.internal_heat_gains import *
from pyMEP.hvac.external_heat_gains import *
from pyMEP.hvac.coolingload import *
from pyMEP.hvac.lighting import *
from pyMEP.hvac.people import *
from pyMEP.hvac.equipment import *
from _resource import *

Q_ = Quantity

class ComfortZone:
	
	_ventilation : Quantity	

	def __init__(self, id: str, weather: WeatherData) -> None:
		self.ID = id		
		self.weather_data = weather
		self.Width : Quantity = Q_(0, 'm')
		self.Length : Quantity = Q_(0, 'm')
		self.Height : Quantity = Q_(0, 'm')
		self.SpaceType : int
		self.safety : Quantity
		self.max_hr : list

		self.Roof : Roof = Roof(id='Roof')
		self.Ceiling : Ceiling = Ceiling(id='Ceiling')
		self.Floor : Floor = Floor(id='Floor')
		self.Wall_A : Wall = Wall(id='Wall_A')
		self.Wall_B : Wall = Wall(id='Wall_B')
		self.Wall_C : Wall = Wall(id='Wall_C')
		self.Wall_D : Wall = Wall(id='Wall_D')

		self.Light_HeatGain = LightingHeatGain(ID="Lighting_0")
		self.Light_HeatGain.add_lighting(SpaceLighting.create(ID="ls0", schedule=self.Light_HeatGain.usage_schedule))
		self.People_HeatGain = PeopleHeatGain('People_0')
		self.Equipment_HeatGain = EquipmentHeatGain('Equipment_0')
		self.Equipment_HeatGain.add_equipment(GenericAppliance.create(ID='eqp0', schedule=self.Equipment_HeatGain.usage_schedule))

		self.external_load_df = pd.DataFrame([i for i in range(24)], columns=['Hr'])
		self.external_load_df.set_index('Hr', inplace=True)
		self.internal_load_df = self.external_load_df.copy()
		self.ventilation_load_df = self.external_load_df.copy()
		self.wall_load_df = self.external_load_df.copy()
		self.window_load_df = self.external_load_df.copy()
		self.cooling_load_df = self.external_load_df.copy()
	
	def Calculate(self) -> None:
		# UPDATE WEATHER DATA
		self.weather_data.update_sun_position()
		self.weather_data.synthetic_daily_db_profiles()
		match self.SpaceType:
			case 0:		# Single Floor
				self.Roof.IsEnabled = True
				self.Floor.IsEnabled = False			
			case 1:		# Highest Floor
				self.Roof.IsEnabled = True
				self.Floor.IsEnabled = True
			case 2:		# Middle Floor
				self.Roof.IsEnabled = False
				self.Floor.IsEnabled = True
			case 3:		# Lowest Floor
				self.Roof.IsEnabled = False
				self.Floor.IsEnabled = False
		self.Ceiling.IsEnabled = not self.Roof.IsEnabled
		Setting.NRTS_zones = 'Exterior' if self.Wall_A.wall_type.value or self.Wall_B.wall_type.value or self.Wall_C.wall_type.value or self.Wall_D.wall_type.value else 'Interior'
		self.ns_rts_zone = RTS.rts_values(nrts=True, zones = Setting.NRTS_zones , 
													 room_construction = Setting.NRTS_Room_construction, 
													 carpet = Setting.NRTS_Carpet, 
													 glass = Setting.NRTS_Glass)
		self.s_rts_zone = RTS.rts_values(nrts=False, room_construction = Setting.NRTS_Room_construction, 
													 carpet = Setting.NRTS_Carpet, 
													 glass = Setting.NRTS_Glass)
		# ROOF
		if not self.Roof.IsEnabled:
			self.Roof.cooling_load_df = None
			self.external_load_df['Roof'] = 0.0
		else:
			self.Roof.Update_ns_rts(self.ns_rts_zone)
			self.external_load_df['Roof'] = self.Roof.cooling_load_df['TOTAL_CL']
		# FLOOR
		self.Floor.Update_ns_rts(self.ns_rts_zone)
		self.Ceiling.cooling_load_df = self.Floor.cooling_load_df.copy()
		if not self.Floor.IsEnabled:			
			self.Floor.cooling_load_df = None
			self.external_load_df['Floor'] = 0.0
		else:
			self.external_load_df['Floor'] = self.Floor.cooling_load_df['TOTAL_CL']
		# CEILING
		if not self.Ceiling.IsEnabled:
			self.Ceiling.cooling_load_df = None
			self.external_load_df['Ceiling'] = 0.0
		else:
			self.external_load_df['Ceiling'] = self.Ceiling.cooling_load_df['TOTAL_CL']
		# WALL
		self.Wall_A.Update_ns_rts(self.ns_rts_zone)
		self.wall_load_df['Wall-A'] = self.Wall_A.cooling_load_df['TOTAL_CL']
		self.Wall_B.Update_ns_rts(self.ns_rts_zone)
		self.wall_load_df['Wall-B'] = self.Wall_B.cooling_load_df['TOTAL_CL']
		self.Wall_C.Update_ns_rts(self.ns_rts_zone)
		self.wall_load_df['Wall-C'] = self.Wall_C.cooling_load_df['TOTAL_CL']
		self.Wall_D.Update_ns_rts(self.ns_rts_zone)
		self.wall_load_df['Wall-D'] = self.Wall_D.cooling_load_df['TOTAL_CL']
		# WINDOW
		if not self.Wall_A.windows:			
			self.window_load_df['Win-A'] = 0.0
		else:
			window = self.Wall_A.windows.get('Win-A')
			window.S_RTS = self.s_rts_zone
			window.update_cooling_load()
			self.window_load_df['Win-A'] = window.cooling_load_df['TOTAL_CL']
		if not self.Wall_B.windows:			
			self.window_load_df['Win-B'] = 0.0
		else:
			window = self.Wall_B.windows.get('Win-B')
			window.S_RTS = self.s_rts_zone
			window.update_cooling_load()
			self.window_load_df['Win-B'] = window.cooling_load_df['TOTAL_CL']
		if not self.Wall_C.windows:			
			self.window_load_df['Win-C'] = 0.0
		else:
			window = self.Wall_C.windows.get('Win-C')
			window.S_RTS = self.s_rts_zone
			window.update_cooling_load()
			self.window_load_df['Win-C'] = window.cooling_load_df['TOTAL_CL']
		if not self.Wall_D.windows:			
			self.window_load_df['Win-D'] = 0.0
		else:
			window = self.Wall_D.windows.get('Win-D')
			window.S_RTS = self.s_rts_zone
			window.update_cooling_load()
			self.window_load_df['Win-D'] = window.cooling_load_df['TOTAL_CL']
		# LIGHTING
		self.Light_HeatGain.Update_ns_rts(self.ns_rts_zone)
		self.internal_load_df['Lighting'] = self.Light_HeatGain.cooling_load_df['TOTAL_CL']
		# PEOPLE
		self.People_HeatGain.Update_ns_rts(self.ns_rts_zone)
		self.internal_load_df['People'] = self.People_HeatGain.cooling_load_df['TOTAL_CL']
		# EQUIPMENT
		self.Equipment_HeatGain.Update_ns_rts(self.ns_rts_zone)
		self.internal_load_df['Equipment'] = self.Equipment_HeatGain.cooling_load_df['TOTAL_CL']
		# VENTILATION
		qs = np.round(self._cs * self._ventilation * (np.array([i.m for i in self.weather_data.T_db_prof]) - Setting.Inside_DB.m), 0)
		self.ventilation_load_df['SHG'] =  qs * np.array(self.Light_HeatGain.usage_profile)
		SetUnitSystem(SI)
		hum_ratio_o = CalcPsychrometricsFromTWetBulb(self.weather_data.T_db_des.m, self.weather_data.T_wb_mc.m, 101325)[0] * 1000
		hum_ratio_i = CalcPsychrometricsFromRelHum(Setting.Inside_DB.m, Setting.Inside_RH, 101325)[0] * 1000
		ql = np.round(self._cl * self._ventilation * (hum_ratio_o - hum_ratio_i), 0)
		self.ventilation_load_df['LHG'] =  ql * np.array(self.Light_HeatGain.usage_profile)
		self.ventilation_load_df['TOTAL_CL'] = self.ventilation_load_df['SHG'] + self.ventilation_load_df['LHG']
		# SUMMARY		
		self.wall_load_df['TOTAL_CL'] = 0.0
		self.wall_load_df['TOTAL_CL'] = self.wall_load_df.sum(axis=1)
		self.external_load_df['Wall'] = self.wall_load_df['TOTAL_CL']
		self.window_load_df['TOTAL_CL'] = 0.0
		self.window_load_df['TOTAL_CL'] = self.window_load_df.sum(axis=1)
		self.external_load_df['Window'] = self.window_load_df['TOTAL_CL']
		self.external_load_df['TOTAL_CL'] = 0.0
		self.external_load_df['TOTAL_CL'] = self.external_load_df.sum(axis=1)
		self.internal_load_df['TOTAL_CL'] = 0.0
		self.internal_load_df['TOTAL_CL'] = self.internal_load_df.sum(axis=1)
		self.cooling_load_df['external'] = self.external_load_df['TOTAL_CL']
		self.cooling_load_df['internal'] = self.internal_load_df['TOTAL_CL']
		self.cooling_load_df['ventilation'] = self.ventilation_load_df['TOTAL_CL']
		self.cooling_load_df['TOTAL_CL'] = 0.0
		self.cooling_load_df['TOTAL_CL'] = self.cooling_load_df.sum(axis=1)		
		total_cl = self.cooling_load_df['TOTAL_CL']
		self.max_hr = total_cl[total_cl == total_cl.max()].index.tolist()
		print('---------- CALCULATED ------------')

	# region
	@property
	def Ventilation(self) -> Quantity:
		return self._ventilation
	@Ventilation.setter
	def Ventilation(self, v: Quantity) -> None:
		# ASHRAE Fundamentals 2021, p18.15 Elevation Correction Examples
		self._ventilation = v.to('m ** 3/second')
		h = self.weather_data.altitude.m
		self._cs = 1230*(1-(h*2.25577*1e-5)) ** 5.2559
		self._cl = 3010*(1-(h*2.25577*1e-5)) ** 5.2559

	@property
	def Area(self) -> Quantity:
		return self.Width * self.Length
	#endregion

if __name__ == "__main__":
	zone_weather = WeatherData()
	zone = ComfortZone('Room 1', weather=zone_weather)
	zone_weather.fi = Q_(33.640, 'deg')
	zone_weather.L_loc = Q_(-84.4, 'deg')
	zone_weather.altitude = Q_(313, 'm')
	zone_weather.T_db_des = Q_(33.1, 'degC')
	zone_weather.T_db_rng = Q_(9.3, 'delta_degC')
	zone_weather.T_wb_mc = Q_(23.2, 'degC')		
	zone_weather.taub =  0.515
	zone_weather.taud = 2.066
	zone_weather.tz = -5
	zone_weather.date = ReferenceDates.get_date_for('jul')
	zone_weather.synthetic_daily_db_profiles()

	Setting.Inside_DB = Q_(float(25), 'degC')
	Setting.Inside_RH = float(55)/100
	zone.SpaceType = 0
	zone.Width = Q_(5.5, 'm')
	zone.Length = Q_(8.0, 'm')
	zone.Height = Q_(3.5, 'm')

	zone.Roof.weather_data = zone_weather
	zone.Roof.net_area = zone.Area
	zone.Roof.U = 1.381
	zone.Roof.CTS = [66.39,32.53,1.05,0.03,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

	zone.Floor.weather_data = zone_weather
	zone.Floor.net_area = zone.Area
	zone.Floor.U = 2.562
	zone.Floor.CTS = [0.72,2.08,6.54,9.54,10.12,9.56,8.6,7.59,6.64,5.78,5.02,4.36,3.79,3.29,2.85,2.48,2.15,1.87,1.62,1.41,1.22,1.06,0.92,0.8]
	zone.Floor.delta_T = Q_(6.7, 'delta_degC')

	zone.Wall_A.weather_data = zone_weather
	zone.Wall_A.psi = Q_(60, 'deg')
	zone.Wall_A.net_area = zone.Height * zone.Length
	zone.Wall_A.U = 3.647
	zone.Wall_A.CTS = [8.07,34.24,25.16,14.27,8.01,4.5,2.52,1.42,0.79,0.45,0.25,0.14,0.08,0.04,0.02,0.01,0.01,0,0,0,0,0,0,0]
	zone.Wall_A.wall_type = Wall.WallType.External
	zone.Wall_A.surface_absorptance = 0.052

	zone.Wall_B.weather_data = zone_weather
	zone.Wall_B.psi = Q_(-30, 'deg')
	zone.Wall_B.net_area = zone.Height * zone.Width
	zone.Wall_B.U = 3.647
	zone.Wall_B.CTS = [8.07,34.24,25.16,14.27,8.01,4.5,2.52,1.42,0.79,0.45,0.25,0.14,0.08,0.04,0.02,0.01,0.01,0,0,0,0,0,0,0]
	zone.Wall_B.wall_type = Wall.WallType.External
	zone.Wall_B.surface_absorptance = 0.052

	zone.Wall_C.weather_data = zone_weather
	zone.Wall_C.psi = Q_(-120, 'deg')
	zone.Wall_C.net_area = zone.Height * zone.Length
	zone.Wall_C.U = 3.647
	zone.Wall_C.wall_type = Wall.WallType.Internal
	zone.Wall_A.delta_T = Q_(6.7, 'delta_degC')

	zone.Wall_D.weather_data = zone_weather
	zone.Wall_D.psi = Q_(150, 'deg')
	zone.Wall_D.net_area = zone.Height * zone.Width
	zone.Wall_D.U = 3.647
	zone.Wall_D.wall_type = Wall.WallType.Internal
	zone.Wall_D.delta_T = Q_(6.7, 'delta_degC')

	win_w = Q_(1.5, 'm')
	win_h = Q_(1.0, 'm')
	zone.Wall_A.add_window(id='Win-A', width=win_w, height=win_h, U=6.23, SC=0.96)
	win = zone.Wall_A.windows.get('Win-A')
	win.SHGCd = [0.81, 0.80, 0.78, 0.73, 0.62, 0.39, 0]
	win.SHGCh = 0.73

	zone_light = zone.Light_HeatGain.get_lighting('ls0')
	zone_light.power_density = Q_(1.2, 'W / m ** 2')
	zone_light.A_floor = zone.Area
	zone_light.F_space = Q_(0.69,'').to('%')
	zone_light.F_rad = Q_(0.58,'').to('%')
	zone.Light_HeatGain.UpdateUsageProfile([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0])	
		
	zone.People_HeatGain.occupants.Q_dot_sen_person = Q_(70, 'W')
	zone.People_HeatGain.occupants.Q_dot_lat_person = Q_(45, 'W')
	zone.People_HeatGain.occupants.F_rad = Q_(60, '%')
	zone.People_HeatGain.UpdateUsageProfile([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0])

	zone.Ventilation = Q_(max(zone.People_HeatGain.usage_profile) * 20, 'cubic_foot/minute')

	zone_equipment = zone.Equipment_HeatGain.get_equipment('eqp0')
	zone_equipment.F_rad = Q_(0.3 * 100, '%')
	zone_equipment.Q_dot_sen_pcs = Q_(zone.Area.m * 8.5, 'W')
	zone_equipment.Q_dot_lat_pcs = Q_(zone.Area.m * 0, 'W')

	zone.Equipment_HeatGain.UpdateUsageProfile([0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0])
	zone.safety = Q_(5,'%')

	print('---------- CALCULATING -----------')
	zone.Calculate()

	i = zone.max_hr[0]
	print(f'Lighting Load @{i} Hour = {zone.internal_load_df[i:i+1]['Lighting'].values[0]:0.2f} Watt')
	print(f'People Load @{i} Hour = {zone.internal_load_df[i:i+1]['People'].values[0]:0.2f} Watt')
	print(f'Equipment Load @{i} Hour = {zone.internal_load_df[i:i+1]['Equipment'].values[0]:0.2f} Watt')

	print(f'Roof Load @{i} Hour = {zone.external_load_df[i:i+1]['Roof'].values[0]:0.2f} Watt')
	print(f'Floor Load @{i} Hour = {zone.external_load_df[i:i+1]['Floor'].values[0]:0.2f} Watt')
	print(f'Ceiling Load @{i} Hour = {zone.external_load_df[i:i+1]['Ceiling'].values[0]:0.2f} Watt')

	print(f'Wall-A Load @{i} Hour = {zone.wall_load_df[i:i+1]['Wall-A'].values[0]:0.2f} Watt')
	print(f'Wall-B Load @{i} Hour = {zone.wall_load_df[i:i+1]['Wall-B'].values[0]:0.2f} Watt')
	print(f'Wall-C Load @{i} Hour = {zone.wall_load_df[i:i+1]['Wall-C'].values[0]:0.2f} Watt')
	print(f'Wall-D Load @{i} Hour = {zone.wall_load_df[i:i+1]['Wall-D'].values[0]:0.2f} Watt')
	print(f'Walls Load @{i} Hour = {zone.wall_load_df[i:i+1]['TOTAL_CL'].values[0]:0.2f} Watt')

	print(f'Win-A Load @{i} Hour = {zone.window_load_df[i:i+1]['Win-A'].values[0]:0.2f} Watt')
	print(f'Win-B Load @{i} Hour = {zone.window_load_df[i:i+1]['Win-B'].values[0]:0.2f} Watt')
	print(f'Win-C Load @{i} Hour = {zone.window_load_df[i:i+1]['Win-C'].values[0]:0.2f} Watt')
	print(f'Win-D Load @{i} Hour = {zone.window_load_df[i:i+1]['Win-D'].values[0]:0.2f} Watt')
	print(f'Windows Load @{i} Hour = {zone.window_load_df[i:i+1]['TOTAL_CL'].values[0]:0.2f} Watt')

	print(f'External Load @{i} Hour = {zone.external_load_df[i:i+1]['TOTAL_CL'].values[0]:0.2f} Watt')
	print(f'Internal Load @{i} Hour = {zone.internal_load_df[i:i+1]['TOTAL_CL'].values[0]:0.2f} Watt')
	print(f'Ventilation Load @{i} Hour = {zone.cooling_load_df[i:i+1]['ventilation'].values[0]:0.2f} Watt')	

	i_total_cl = zone.cooling_load_df[i:i+1]['TOTAL_CL'].values[0]
	i_safety = i_total_cl * zone.safety.to('').m
	i_total = i_total_cl + i_safety
	print(f'Safety = {i_safety:0.2f} Watt')	
	print(f'Total Load @{i} Hour = {i_total:0.2f} Watt')