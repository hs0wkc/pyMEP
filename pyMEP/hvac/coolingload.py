from dataclasses import dataclass
import numpy as np
import pandas as pd
from .. import Quantity

Q_ = Quantity

@dataclass
class Setting:
	Inside_DB = Q_(25, 'degC')
	Inside_RH = 0.55
	delta_T = Q_(6.7, 'delta_degC')
	rho = 0.2						# ASHRAE Fundamentals 2021 p14.12 Ground Reflectance of Foreground Surfaces
	vlwc = 0						# ASHRAE Fundamentals 2021 p18.24 Vertical Surface Long-wave correction
	hlwc = 4						# ASHRAE Fundamentals 2021 p18.24 Horizontal Surface Long-wave correction	
	surface_absorptance = 0.052		# ASHRAE Fundamentals 2021 p18.25 Table 15 Solar Absorptance Values of Various Surfaces

	NRTS_zones : str = 'Exterior'
	NRTS_Room_construction : str ='Medium'
	NRTS_Carpet : str = 'No Carpet'
	NRTS_Glass : str ='50%'
	
	# from ASHRAE Fundamentals 2021, Chapter 18, §18.6
	# Table 3 Lighting Heat Gain Parameters for Typical Operating Conditions
	# Lighting_F_rad = 0.5			# Non-in-ceiling fluorescent surface-mounted luminaire
	# Lighting_F_space = 1.0		# Non-in-ceiling fluorescent luminaire
	Lighting_F_rad = 0.58			# Recessed fluorescent luminaire without lens
	Lighting_F_space = 0.69			# Recessed fluorescent luminaire without lens
	Lighting_F_use = 1.0	

	lighting_location : str = 'Office'
	lighting_category : str = 'Enclosed'
	people_activity : str = 'Seated, very light work'
	people_location : str = 'Office'	

	"""from ASHRAE Fundamentals 2021 p18.24
	Table 14 Recommended Radiative/Convective Splits for Internal Heat Gains"""
	Wall_F_rad = 0.46				# Conduction heat gain - Through walls and floors
	Roof_F_rad = 0.6
	Window_hshgc_F_rad = 0.33		# SHGC > 0.5
	Window_lshgc_F_rad = 0.46		# SHGC < 0.5
	Equipment_Generic_F_rad = 0.3	# Equipment 0.1 to 0.8
	OfficeEquipment_F_rad = 0.3

	tsm_export = False

@dataclass
class RTS:
	# ASHRAE Fundamentals 2021, Chapter 18, §18.38
	# Tables 19 Representative Nonsolar RTS Values for Light to Heavy Construction
	nonsolar_rts_df = pd.DataFrame([
		[0  ,47 ,50 ,53 ,41 ,43 ,46 ,46 ,49 ,52 ,31 ,33 ,35 ,34 ,38 ,42 ,22 ,25 ,28 ,46 ,40 ,46 ,31 ,33 ,21],
		[1  ,19 ,18 ,17 ,20 ,19 ,19 ,18 ,17 ,16 ,17 ,16 ,15 ,9  ,9  ,9  ,10 ,9  ,9  ,19 ,20 ,18 ,17 ,9  ,9 ],
		[2  ,11 ,10 ,9  ,12 ,11 ,11 ,10 ,9  ,8  ,11 ,10 ,10 ,6  ,6  ,5  ,6  ,6  ,6  ,11 ,12 ,10 ,11 ,6  ,6 ],
		[3  ,6  ,6  ,5  ,8  ,7  ,7  ,6  ,5  ,5  ,8  ,7  ,7  ,4  ,4  ,4  ,5  ,5  ,5  ,6  ,8  ,6  ,8  ,5  ,5 ],
		[4  ,4  ,4  ,3  ,5  ,5  ,5  ,4  ,3  ,3  ,6  ,5  ,5  ,4  ,4  ,4  ,5  ,5  ,4  ,4  ,5  ,3  ,6  ,4  ,5 ],
		[5  ,3  ,3  ,2  ,4  ,3  ,3  ,2  ,2  ,2  ,4  ,4  ,4  ,4  ,3  ,3  ,4  ,4  ,4  ,3  ,4  ,2  ,4  ,4  ,4 ],
		[6  ,2  ,2  ,2  ,3  ,3  ,2  ,2  ,2  ,2  ,4  ,3  ,3  ,3  ,3  ,3  ,4  ,4  ,4  ,2  ,3  ,2  ,4  ,3  ,4 ],
		[7  ,2  ,1  ,1  ,2  ,2  ,2  ,1  ,1  ,1  ,3  ,3  ,3  ,3  ,3  ,3  ,4  ,4  ,4  ,2  ,2  ,1  ,3  ,3  ,4 ],
		[8  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,3  ,2  ,2  ,3  ,3  ,3  ,4  ,3  ,3  ,1  ,1  ,1  ,3  ,3  ,4 ],
		[9  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,3  ,3  ,2  ,3  ,3  ,3  ,1  ,1  ,1  ,2  ,3  ,3 ],
		[10 ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,3  ,2  ,2  ,3  ,3  ,3  ,1  ,1  ,1  ,2  ,3  ,3 ],
		[11 ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,2  ,3  ,3  ,3  ,1  ,1  ,1  ,2  ,2  ,3 ],
		[12 ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,3  ,3  ,3  ,1  ,1  ,1  ,1  ,2  ,3 ],
		[13 ,1  ,1  ,1  ,0  ,1  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,3  ,3  ,2  ,1  ,1  ,1  ,1  ,2  ,3 ],
		[14 ,0  ,0  ,1  ,0  ,1  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,3  ,2  ,2  ,1  ,0  ,1  ,1  ,2  ,3 ],
		[15 ,0  ,0  ,1  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,2  ,0  ,0  ,1  ,1  ,2  ,3 ],
		[16 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,2  ,0  ,0  ,1  ,1  ,2  ,3 ],
		[17 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,2  ,0  ,0  ,1  ,1  ,2  ,2 ],
		[18 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,1  ,2  ,2  ,2  ,0  ,0  ,1  ,1  ,2  ,2 ],
		[19 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,0  ,0  ,1  ,1  ,2  ,2  ,1  ,2  ,2  ,2  ,0  ,0  ,1  ,0  ,2  ,2 ],
		[20 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,2  ,1  ,1  ,2  ,2  ,2  ,0  ,0  ,0  ,0  ,2  ,2 ],
		[21 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,2  ,1  ,1  ,2  ,2  ,2  ,0  ,0  ,0  ,0  ,2  ,2 ],
		[22 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,0  ,1  ,1  ,1  ,2  ,2  ,2  ,0  ,0  ,0  ,0  ,1  ,2 ],
		[23 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,2  ,2  ,1  ,0  ,0  ,0  ,0  ,1  ,2 ]])

	# ASHRAE Fundamentals 2021, Chapter 18, §18.38
	# Tables 20 Representative Solar RTS Values for Light to Heavy Construction
	solar_rts_df = pd.DataFrame([
		[0  ,53 ,55 ,56 ,44 ,45 ,46 ,52 ,54 ,55 ,28 ,29 ,29 ,47 ,49 ,51 ,26 ,27 ,28],
		[1  ,17 ,17 ,17 ,19 ,20 ,20 ,16 ,16 ,15 ,15 ,15 ,15 ,11 ,12 ,12 ,12 ,13 ,13],
		[2  ,9  ,9  ,9  ,11 ,11 ,11 ,8  ,8  ,8  ,10 ,10 ,10 ,6  ,6  ,6  ,7  ,7  ,7 ],
		[3  ,5  ,5  ,5  ,7  ,7  ,7  ,5  ,4  ,4  ,7  ,7  ,7  ,4  ,4  ,3  ,5  ,5  ,5 ],
		[4  ,3  ,3  ,3  ,5  ,5  ,5  ,3  ,3  ,3  ,6  ,6  ,6  ,3  ,3  ,3  ,4  ,4  ,4 ],
		[5  ,2  ,2  ,2  ,3  ,3  ,3  ,2  ,2  ,2  ,5  ,5  ,5  ,2  ,2  ,2  ,4  ,4  ,4 ],
		[6  ,2  ,2  ,2  ,3  ,2  ,2  ,2  ,1  ,1  ,4  ,4  ,4  ,2  ,2  ,2  ,3  ,3  ,3 ],
		[7  ,1  ,1  ,1  ,2  ,2  ,2  ,1  ,1  ,1  ,4  ,3  ,3  ,2  ,2  ,2  ,3  ,3  ,3 ],
		[8  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,3  ,3  ,3  ,2  ,2  ,2  ,3  ,3  ,3 ],
		[9  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,3  ,3  ,3  ,2  ,2  ,2  ,3  ,3  ,3 ],
		[10 ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,2  ,3  ,3  ,3 ],
		[11 ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,2  ,1  ,3  ,3  ,2 ],
		[12 ,1  ,1  ,1  ,1  ,1  ,0  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,1  ,1  ,2  ,2  ,2 ],
		[13 ,1  ,1  ,0  ,1  ,0  ,0  ,1  ,1  ,1  ,2  ,2  ,2  ,2  ,1  ,1  ,2  ,2  ,2 ],
		[14 ,1  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,1  ,1  ,2  ,2  ,2 ],
		[15 ,1  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[16 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[17 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[18 ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[19 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[20 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[21 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,2  ,2  ,2 ],
		[22 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,2  ,1  ,1 ],
		[23 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,0  ,1  ,1  ,1  ,2  ,1  ,1 ]])

	Zones = ('Exterior', 'Interior')					# 'Exterior' or 'Interior'
	Room_construction = ('Light', 'Medium', 'Heavy')
	Carpet = ('With Carpet', 'No Carpet')
	Glass = ('10%', '50%', '90%')

	@classmethod
	def rts_values(cls,
				   nrts:bool = True, 
				   zones:str = 'Exterior', 
				   room_construction:str='Medium', 
				   carpet:str='No Carpet', 
				   glass:str = '50%') -> pd.DataFrame:
		df = cls.nonsolar_rts_df if nrts else cls.solar_rts_df
		isExterior = not(nrts) or cls.Zones.index(zones)==0
		index = 1 + (0 if zones is None else cls.Zones.index(zones) * 18)
		index += cls.Room_construction.index(room_construction) * (6 if isExterior else 2)
		index += cls.Carpet.index(carpet) * (3 if isExterior else 1)
		index += (cls.Glass.index(glass) if glass in cls.Glass else 0) if isExterior else 0
		rts_df = df.iloc[:, index:(index+1)]
		rts_df.columns = ['NS-RTS' if nrts else 'S-RTS']
		return rts_df

def TimeSeriesMethod(ts:list, heat_load:list, id:str = 'id', tstype:str = 'Tx') -> pd.Series:
	"""Load ที่เกิดขึ้นในแต่ละชั่วโมงจะถูกนำไปคูณกับ ts เพื่อกระจายเป็น load ในชั่วโมงถัดๆไป เช่น Load ที่เกิดขึ้นตอน 7 โมงเช้ามีค่า 260 Watt
	ถ้า ts ที่เลือกใช้เป็น [49, 17, 9, 5, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 ,0, 0]
	เมื่อนำไปคูณกับ ts จะได้ [127.4, 44.2, 23.4, 13, 7.8, 5.2, 5.2, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 2.6, 0, 0, 0, 0]
	ซึ่งจะกลายเป็น Load ที่ตกค้างไปมีผลในชั่วโมงถัดไป นั้้นคือจะมี Load 127.4W ตอน 7:00AM และตอน 8:00AM จะมีโหลดตกค้างอยู่อีก 44.2W 23.4W ในตอน 9:0AM 
	ไล่ไปในชั่วโมงถัดไปตามลำดีบ ในบางครั้งถ้า Load ที่เกิดขึ้นเป็นตอนสามทุ่ม ภาระความร้อนก็จะมีผลไปจนถึงห้าโมงเย็นของวันถัดไป"""
	def __FillDown(ilist, row, column):
		for i in range(24):
			df.iat[row+i, column] = ilist[i]

	rts_array = np.array(ts)/100
	df = pd.DataFrame(np.nan, index=range(48), columns=range(24))
	for i in range(24):
		cooling_load_array = rts_array * heat_load[i]
		__FillDown(cooling_load_array, i, i)
	sum_list = []
	for i in range(48):
		sum_list.append(df.iloc[i].sum(axis=0))
	sum_df = pd.DataFrame(sum_list, columns=['S1'])
	df = pd.concat([df, sum_df], axis=1)
	half_sum_df = pd.DataFrame(sum_list[24:], columns=['S2'])
	df = pd.concat([df, half_sum_df], axis=1)
	dfx = df['S1'][0:24] + df['S2'][0:24]
	df.insert(loc=26, column='Q_o', value=dfx)
	df.insert(loc=0, column='Q_i', value=heat_load+([np.nan] * 24))
	df.insert(loc=0, column=tstype, value=ts+([np.nan] * 24))
	if Setting.tsm_export: 
		try:
			df.to_excel(id+'.'+tstype+'_tsm.xlsx')
		except PermissionError: ...
	return dfx
