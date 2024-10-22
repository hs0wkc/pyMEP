import pandas as pd
from dataclasses import dataclass
from math import floor
from iapws import IAPWS97

def _upper_bound(x, list_data):
    if  x > list_data[-1]:
        return
    for i, y in enumerate(list_data):
        if x <= y:
            return list_data[i], i
def _lower_bound(x, list_data):
    if  x < list_data[0]:
        return
    for i, y in enumerate(reversed(list_data)):
        if x >= y:
            return list_data[-i-1], list_data.index(y)

@dataclass(frozen=True)
class WATER():

	@classmethod
	def hf(cls, temperature:float = 1) -> float|None:
		# Specific Enthalpy of Water (hf)
		return IAPWS97(T=temperature + 273.15, x=0).h

@dataclass(frozen=True)
class STEAM():
	# https://iapws.readthedocs.io/en/latest/iapws.iapws97.html#iapws.iapws97.IAPWS97
	# x : x (float) – Vapor quality
	# Parameter : pressure (bar.a)
	@classmethod
	def SaturationTemperature(cls, pressure:float = 1) -> float|None:
		# Specific Enthalpy of Evaporation (hfg)
		return IAPWS97(P=pressure/10, x=0).T -273.15

	@classmethod
	def hf(cls, pressure:float = 1) -> float|None:
		# Specific Enthalpy of Water (hf)
		return IAPWS97(P=pressure/10, x=0).h

	@classmethod
	def hfg(cls, pressure:float = 1) -> float|None:
		# Specific Enthalpy of Evaporation (hfg)
		return cls.hg(pressure) - cls.hf(pressure)

	@classmethod
	def hg(cls, pressure:float = 1) -> float|None:
		# Specific Enthalpy of Steam (hg)
		return IAPWS97(P=pressure/10, x=1).h

	@classmethod
	def Density(cls, pressure:float = 1) -> float|None:
		# Specific Entropy of Water (sf)
		return IAPWS97(P=pressure/10, x=1).rho

	@classmethod
	def Vg(cls, pressure:float = 1) -> float|None:
		# Specific Volume of Steam (vg)		
		return IAPWS97(P=pressure/10, x=1).v

	@classmethod
	def Sf(cls, pressure:float = 1) -> float|None:
		# Specific Entropy of Water (sf)
		return IAPWS97(P=pressure/10, x=0).s

	@classmethod
	def Sfg(cls, pressure:float = 1) -> float|None:
		# Specific Entropy of Evaporation (sfg)
		return cls.Sg(pressure) - cls.Sf(pressure)

	@classmethod
	def Sg(cls, pressure:float = 1) -> float|None:
		# Specific Entropy of Steam (sg)
		return IAPWS97(P=pressure/10, x=1).s

	@classmethod
	def Cv(cls, pressure:float = 1) -> float|None:
		# Specific Heat of Steam at Constant Volume (cv)
		return IAPWS97(P=pressure/10, x=1).cv

	@classmethod
	def Cp(cls, pressure:float = 1) -> float|None:
		# Specific Heat of Steam at Constant Pressure (cp)
		return IAPWS97(P=pressure/10, x=1).cp

	@classmethod
	def DynamicViscosity(cls, pressure:float = 1) -> float|None:
		# Dynamic viscosity, [Pa·s]
		return IAPWS97(P=pressure/10, x=1).mu

@dataclass(frozen=True)
class FUEL():
	property_table = {'LPG':			[50220,'kj/kg'],
					  'Fuel Oil Gr.A':	[41274,'kj/Litre'], 
					  'Fuel Oil Gr.C':	[38174,'kj/Litre'],
					  'Bituminous Gr.A':[32564,'kj/kg'],
					  'Bituminous Gr.C':[24423,'kj/kg'],
					  'Wood Pellets':	[17000,'kj/kg']}

	@classmethod
	def FuelList(cls):
		fuel_list = list(cls.property_table.keys())
		return fuel_list

	@classmethod
	def FuelGCV(cls, fuel):
		return cls.property_table[fuel][0]

	@classmethod
	def FuelUnit(cls, fuel):
		return cls.property_table[fuel][1]

@dataclass(frozen=True)
class LPG():

	@classmethod
	def GetPipeSize(cls, df: pd.DataFrame, length:float, btu:float) -> str:
		length_list = df['Length'].tolist()
		length_th = _upper_bound(length, length_list)[1]
		btu_list = df[length_th:length_th+1].values.flatten().tolist()
		btu_list.pop(0)
		btu_th = _upper_bound(btu, btu_list)[1]
		return df.columns.tolist()[btu_th+1]

	LPG10_1_df = pd.DataFrame([
				[  10, 3320, 6950,13100, 26900, 40300, 77600,124000, 219000, 446000],
				[  20, 2280, 4780, 9000, 18500, 27700, 53300, 85000, 150000, 306000],
				[  30, 1830, 3840, 7220, 14800, 22200, 42800, 68200, 121000, 246000],
				[  40, 1570, 3280, 6180, 12700, 19000, 36600, 58400, 103000, 211000],
				[  50, 1390, 2910, 5480, 11300, 16900, 32500, 51700,  91500, 187000],
				[  60, 1260, 2640, 4970, 10200, 15300, 29400, 46900,  82900, 169000],
				[  70, 1160, 2430, 4570,  9380, 14100, 27100, 43100,  76300, 156000],
				[  80, 1080, 2260, 4250,  8730, 13100, 25200, 40100,  70900, 145000],
				[  90, 1010, 2120, 3990,  8190, 12300, 23600, 37700,  66600, 136000],
				[ 100,  956, 2000, 3770,  7730, 11600, 22300, 35600,  62900, 128000],
				[ 125,  848, 1770, 3340,  6850, 10300, 19800, 31500,  55700, 114000],
				[ 150,  768, 1610, 3020,  6210,  9300, 17900, 28600,  50500, 103000],
				[ 175,  706, 1480, 2780,  5710,  8560, 16500, 26300,  46500,  94700],
				[ 200,  657, 1370, 2590,  5320,  7960, 15300, 24400,  43200,  88100],
				[ 250,  582, 1220, 2290,  4710,  7060, 13600, 21700,  38300,  78100],
				[ 300,  528, 1100, 2080,  4270,  6400, 12300, 19600,  34700,  70800],
				[ 350,  486, 1020, 1910,  3930,  5880, 11300, 18100,  31900,  65100],
				[ 400,  452,  945, 1780,  3650,  5470, 10500, 16800,  29700,  60600],
				[ 450,  424,  886, 1670,  3430,  5140,  9890, 15800,  27900,  56800],
				[ 500,  400,  837, 1580,  3240,  4850,  9340, 14900,  26300,  53700],
				[ 550,  380,  795, 1500,  3070,  4610,  8870, 14100,  25000,  51000],
				[ 600,  363,  759, 1430,  2930,  4400,  8460, 13500,  23900,  48600],
				[ 650,  347,  726, 1370,  2810,  4210,  8110, 12900,  22800,  46600],
				[ 700,  334,  698, 1310,  2700,  4040,  7790, 12400,  21900,  44800],
				[ 750,  321,  672, 1270,  2600,  3900,  7500, 12000,  21100,  43100],
				[ 800,  310,  649, 1220,  2510,  3760,  7240, 11500,  20400,  41600],
				[ 850,  300,  628, 1180,  2430,  3640,  7010, 11200,  19800,  40300],
				[ 900,  291,  609, 1150,  2360,  3530,  6800, 10800,  19200,  39100],
				[ 950,  283,  592, 1110,  2290,  3430,  6600, 10500,  18600,  37900],
				[1000,  275,  575, 1080,  2230,  3330,  6420, 10200,  18100,  36900],
				[1100,  261,  546, 1030,  2110,  3170,  6100,  9720,  17200,  35000],
				[1200,  249,  521,  982,  2020,  3020,  5820,  9270,  16400,  33400],
				[1300,  239,  499,  940,  1930,  2890,  5570,  8880,  15700,  32000],
				[1400,  229,  480,  903,  1850,  2780,  5350,  8530,  15100,  30800],
				[1500,  221,  462,  870,  1790,  2680,  5160,  8220,  14500,  29600],
				[1600,  213,  446,  840,  1730,  2590,  4980,  7940,  14000,  28600],
				[1700,  206,  432,  813,  1670,  2500,  4820,  7680,  13600,  27700],
				[1800,  200,  419,  789,  1620,  2430,  4670,  7450,  13200,  26900],
				[1900,  194,  407,  766,  1570,  2360,  4540,  7230,  12800,  26100],
				[2000,  189,  395,  745,  1530,  2290,  4410,  7030,  12400,  25400]],
		columns=['Length','15 mm','20 mm','25 mm','32 mm','40 mm','50 mm','65 mm','80 mm','100 mm'])
	LPG10_3_df = pd.DataFrame([		
				[  10, 5890,12300, 23200, 47600, 71300,137000, 219000, 387000, 789000],
				[  20, 4050, 8460, 15900, 32700, 49000, 94400, 150000, 266000, 543000],
				[  30, 3250, 6790, 12800, 26300, 39400, 75800, 121000, 214000, 436000],
				[  40, 2780, 5810, 11000, 22500, 33700, 64900, 103000, 183000, 373000],
				[  50, 2460, 5150,  9710, 19900, 29900, 57500,  91600, 162000, 330000],
				[  60, 2230, 4670,  8790, 18100, 27100, 52100,  83000, 147000, 299000],
				[  70, 2050, 4300,  8090, 16600, 24900, 47900,  76400, 135000, 275000],
				[  80, 1910, 4000,  7530, 15500, 23200, 44600,  71100, 126000, 256000],
				[  90, 1790, 3750,  7060, 14500, 21700, 41800,  66700, 118000, 240000],
				[ 100, 1690, 3540,  6670, 13700, 20500, 39500,  63000, 111000, 227000],
				[ 125, 1500, 3140,  5910, 12100, 18200, 35000,  55800,  98700, 201000],
				[ 150, 1360, 2840,  5360, 11000, 16500, 31700,  50600,  89400, 182000],
				[ 175, 1250, 2620,  4930, 10100, 15200, 29200,  46500,  82300, 167800],
				[ 200, 1160, 2430,  4580,  9410, 14100, 27200,  43300,  76500, 156100],
				[ 250, 1030, 2160,  4060,  8340, 12500, 24100,  38400,  67800, 138400],
				[ 300,  935, 1950,  3680,  7560, 11300, 21800,  34800,  61500, 125400],
				[ 350,  860, 1800,  3390,  6950, 10400, 20100,  32000,  56500, 115300],
				[ 400,  800, 1670,  3150,  6470,  9690, 18700,  29800,  52600, 107300],
				[ 450,  751, 1570,  2960,  6070,  9090, 17500,  27900,  49400, 100700],
				[ 500,  709, 1480,  2790,  5730,  8590, 16500,  26400,  46600,  95100],
				[ 550,  673, 1410,  2650,  5450,  8160, 15700,  25000,  44300,  90300],
				[ 600,  642, 1340,  2530,  5200,  7780, 15000,  23900,  42200,  86200],
				[ 650,  615, 1290,  2420,  4980,  7450, 14400,  22900,  40500,  82500],
				[ 700,  591, 1240,  2330,  4780,  7160, 13800,  22000,  38900,  79300],
				[ 750,  569, 1190,  2240,  4600,  6900, 13300,  21200,  37400,  76400],
				[ 800,  550, 1150,  2170,  4450,  6660, 12800,  20500,  36200,  73700],
				[ 850,  532, 1110,  2100,  4300,  6450, 12400,  19800,  35000,  71400],
				[ 900,  516, 1080,  2030,  4170,  6250, 12000,  19200,  33900,  69200],
				[ 950,  501, 1050,  1970,  4050,  6070, 11700,  18600,  32900,  67200],
				[1000,  487, 1020,  1920,  3940,  5900, 11400,  18100,  32000,  65400],
				[1100,  463,  968,  1820,  3740,  5610, 10800,  17200,  30400,  62100],
				[1200,  442,  923,  1740,  3570,  5350, 10300,  16400,  29000,  59200],
				[1300,  423,  884,  1670,  3420,  5120,  9870,  15700,  27800,  56700],
				[1400,  406,  849,  1600,  3280,  4920,  9480,  15100,  26700,  54500],
				[1500,  391,  818,  1540,  3160,  4740,  9130,  14600,  25700,  52500],
				[1600,  378,  790,  1490,  3060,  4580,  8820,  14100,  24800,  50700],
				[1700,  366,  765,  1440,  2960,  4430,  8530,  13600,  24000,  49000],
				[1800,  355,  741,  1400,  2870,  4300,  8270,  13200,  23300,  47600],
				[1900,  344,  720,  1360,  2780,  4170,  8040,  12800,  22600,  46200],
				[2000,  335,  700,  1320,  2710,  4060,  7820,  12500,  22000,  44900]],
		columns=['Length','15 mm','20 mm','25 mm','32 mm','40 mm','50 mm','65 mm','80 mm','100 mm'])
	LPG2_1_df = pd.DataFrame([		
				[  10, 413, 852, 1730, 3030, 4300, 9170, 16500, 26000, 54200],
				[  20, 284, 585, 1190, 2080, 2950, 6310, 11400, 17900, 37300],
				[  30, 228, 470,  956, 1670, 2370, 5060,  9120, 14400, 29900],
				[  40, 195, 402,  818, 1430, 2030, 4330,  7800, 12300, 25600],
				[  50, 173, 356,  725, 1270, 1800, 3840,  6920, 10900, 22700],
				[  60, 157, 323,  657, 1150, 1630, 3480,  6270,  9880, 20600],
				[  70, 144, 297,  605, 1060, 1500, 3200,  5760,  9090, 18900],
				[  80, 134, 276,  562,  983, 1390, 2980,  5360,  8450, 17600],
				[  90, 126, 259,  528,  922, 1310, 2790,  5030,  7930, 16500],
				[ 100, 119, 245,  498,  871, 1240, 2640,  4750,  7490, 15600],
				[ 125, 105, 217,  442,  772, 1100, 2340,  4210,  6640, 13800],
				[ 150,  95, 197,  400,  700,  992, 2120,  3820,  6020, 12500],
				[ 175,  88, 181,  368,  644,  913, 1950,  3510,  5540, 11500],
				[ 200,  82, 168,  343,  599,  849, 1810,  3270,  5150, 10700],
				[ 250,  72, 149,  304,  531,  753, 1610,  2900,  4560,  9510],
				[ 300,  66, 135,  275,  481,  682, 1460,  2620,  4140,  8610],
				[ 350,  60, 124,  253,  442,  628, 1340,  2410,  3800,  7920],
				[ 400,  56, 116,  235,  411,  584, 1250,  2250,  3540,  7370],
				[ 450,  53, 109,  221,  386,  548, 1170,  2110,  3320,  6920],
				[ 500,  50, 103,  209,  365,  517, 1110,  1990,  3140,  6530],
				[ 550,  47,  97,  198,  346,  491, 1050,  1890,  2980,  6210],
				[ 600,  45,  93,  189,  330,  469, 1000,  1800,  2840,  5920],
				[ 650,  43,  89,  181,  316,  449,  959,  1730,  2720,  5670],
				[ 700,  41,  86,  174,  304,  431,  921,  1660,  2620,  5450],
				[ 750,  40,  82,  168,  293,  415,  888,  1600,  2520,  5250],
				[ 800,  39,  80,  162,  283,  401,  857,  1540,  2430,  5070],
				[ 850,  37,  77,  157,  274,  388,  829,  1490,  2350,  4900],
				[ 900,  36,  75,  152,  265,  376,  804,  1450,  2280,  4750],
				[ 950,  35,  72,  147,  258,  366,  781,  1410,  2220,  4620],
				[1000,  34,  71,  143,  251,  356,  760,  1370,  2160,  4490],
				[1100,  32,  67,  136,  238,  338,  721,  1300,  2050,  4270],
				[1200,  31,  64,  130,  227,  322,  688,  1240,  1950,  4070],
				[1300,  30,  61,  124,  217,  309,  659,  1190,  1870,  3900],
				[1400,  28,  59,  120,  209,  296,  633,  1140,  1800,  3740],
				[1500,  27,  57,  115,  201,  286,  610,  1100,  1730,  3610],
				[1600,  26,  55,  111,  194,  276,  589,  1060,  1670,  3480],
				[1700,  26,  53,  108,  188,  267,  570,  1030,  1620,  3370],
				[1800,  25,  51,  104,  182,  259,  553,  1000,  1570,  3270],
				[1900,  24,  50,  101,  177,  251,  537,   966,  1520,  3170],
				[2000,  23,  48,   99,  172,  244,  522,   940,  1480,  3090]],
		columns=['Length','8 mm','10 mm','15 mm','18 mm','20 mm','25 mm','32 mm','40 mm','50 mm'])

@dataclass(frozen=True)
class PIPE():

	@classmethod
	def GetPipeSize(cls, d:float, sch:str='40') -> str:
		for p in cls.NPS:
			if ((cls.OutsideDiameter(p) - 2*cls.Thickness(p, sch))/1000) >= floor(d * 1000)/1000.0:
				break
		return p

	@classmethod
	def Thickness(cls, nps:str, sch:str = '40') -> float|None:		
		return cls.PipeThickness_df[cls.PipeThickness_df['nps'].str.match(nps)][sch].values[0]

	@classmethod
	def OutsideDiameter(cls, nps:str) -> float|None:		
		return cls.PipeThickness_df[cls.PipeThickness_df['nps'].str.match(nps)]['OD'].values[0]

	NPS:tuple = ('15 mm', '20 mm', '25 mm', '32 mm', '40 mm', '50 mm', '65 mm', '80 mm', '100 mm', '125 mm', '150 mm', '200 mm', '250 mm', '300 mm')
	PipeThickness_df = pd.DataFrame([
				['10 mm'  , 17.1 , None, 1.65, None, None, None,  2.31, 2.31,  2.31,  None,   3.2,   3.2,   3.2,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['15 mm'  , 21.3 , 1.65, 2.11, None, None, None,  2.77, 2.77,  2.77,  None,  3.73,  3.73,  3.73,  None,  None,  None,  4.78,  7.47,  None,  None,  None,  None],
				['20 mm'  , 26.7 , 1.65, 2.11, None, None, None,  2.87, 2.87,  2.87,  None,  3.91,  3.91,  3.91,  None,  None,  None,  5.56,  7.82,  None,  None,  None,  None],
				['25 mm'  , 33.4 , 1.65, 2.77, None, None, None,  3.38, 3.38,  3.38,  None,  4.55,  4.55,  4.55,  None,  None,  None,  6.35,  9.09,  None,  None,  None,  None],
				['32 mm'  , 42.2 , 1.65, 2.77, None, None, None,  3.56, 3.56,  3.56,  None,  4.85,  4.85,  4.85,  None,  None,  None,  6.35,   9.7,  None,  None,  None,  None],
				['40 mm'  , 48.3 , 1.65, 2.77, None, None, None,  3.68, 3.68,  3.68,  None,  5.08,  5.08,  5.08,  None,  None,  None,  7.14, 10.15,  None,  None,  None,  None],
				['50 mm'  , 60.3 , 1.65, 2.77, None, None, None,  3.91, 3.91,  3.91,  None,  5.54,  5.54,  5.54,  None,  None,  None,  8.74, 11.07, 12.59,  None,  None,  None],
				['65 mm'  , 73   , 2.11, 3.05, None, None, None,  5.16, 5.16,  5.16,  None,  7.01,  7.01,  7.01,  None,  None,  None,  9.53, 14.02, 15.46,  None,  None,  None],
				['80 mm'  , 88.9 , 2.11, 3.05, None, None, None,  5.49, 5.49,  5.49,  None,  7.62,  7.62,  7.62,  None,  None,  None, 11.13, 15.24, 18.55,  None,  None,  None],
				['100 mm' , 114.3, 2.11, 3.05, None, None, None,  6.02, 6.02,  6.02,  None,  8.56,  8.56,  8.56,  None, 11.13,  None, 13.49, 17.12, 24.73,  None,  None,  None],
				['125 mm' , 141.3, 2.77,  3.4, None, None, None,  6.55, 6.55,  6.55,  None,  9.53,  9.53,  9.53,  None,  12.7,  None, 15.88, 19.05,  None,  None,  None,  None],
				['150 mm' , 168.3, 2.77,  3.4, None, None, None,  7.11, 7.11,  7.11,  None, 10.97, 10.97, 10.97,  None, 14.27,  None, 18.26, 21.95, 23.38, 37.10,  None,  None],
				['200 mm' , 219.1, 2.77, 3.75, None, 6.35, 7.04,  8.18, 8.18,  8.18, 10.31,  12.7,  12.7,  12.7, 15.09, 18.26, 20.62, 23.01, 22.23, 22.49, 23.12, 29.96, 49.47],
				['250 mm' , 273.1,  3.4, 4.19, None, 6.35,  7.8,  9.27, 9.27,  9.27,  12.7,  12.7,  12.7, 15.09, 18.26, 21.44,  25.4, 28.58,  25.4, 27.65,  None, 36.96, 61.84],
				['300 mm' , 323.9, 3.96, 4.57, None, 6.35, 8.38,  9.53, 9.52, 10.31, 14.27,  12.7,  12.7, 17.48, 21.44,  25.4, 28.58, 33.32,  25.4, 32.49,  None, 43.54,  None],
				['350 mm' , 355.6, 3.96, 4.78, 6.35, 7.92, 9.53,  9.53, None, 11.13, 15.09,  12.7,  None, 19.05, 23.83, 27.79, 31.75, 35.71,  None, 35.52, 38.89,  None,  None],
				['400 mm' , 406.4, 4.19, 4.78, 6.35, 7.92, 9.53,  9.53, None,  12.7, 16.66,  12.7,  None, 21.44, 26.19, 30.96, 36.53, 40.49,  None,  None, 44.45,  None,  None],
				['500 mm' , 508  , 4.78, 5.54, 6.35, 9.53, 12.7,  9.53, None, 15.09, 20.62,  12.7,  None, 26.19, 32.54,  38.1, 44.45, 50.01,  None,  None,  77.8,  None,  None],
				['550 mm' , 558.8, 4.78, 5.54, 6.35, 9.53, 12.7,  9.53, None,  None, 22.23,  12.7,  None, 28.58, 34.93, 41.28, 47.36, 53.98,  None,  None,  None,  None,  None],
				['600 mm' , 609.6, 5.54, 6.35, 6.35, 9.53,14.27,  9.53, None, 17.48, 24.61,  12.7,  None, 30.96, 38.89, 46.02, 52.37, 59.54,  None,  None,  None,  None,  None],
				['650 mm' , 660.4, None, None, 7.92, 12.7, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['700 mm' , 711.2, None, None, 7.92, 12.7,15.88,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['750 mm' , 762  , 6.35, 7.92, 7.92, 12.7,15.88,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['800 mm' , 812.8, None, None, 7.92, 12.7,15.88,  9.53, None, 17.48,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['850 mm' , 863.6, None, None, 7.92, 12.7,15.88,  9.53, None, 17.48,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['900 mm' , 914.4, None, None, 7.92, 12.7,15.88,  9.53, None, 19.05,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['950 mm' , 965.2, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['1000 mm',  1016, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['1050 mm',1066.8, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['1100 mm',1117.8, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['1150 mm',1168.4, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None],
				['1200 mm',1219.2, None, None, None, None, None,  9.53, None,  None,  None,  12.7,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None]],
		columns=['nps'	  ,'OD'	 , '5S', '10S', '10', '20', '30','STD','40S',  '40',   '60', 'XS', '80S',   '80','100', '120', '140', '160', 'XXS', 'DXS', 'DXXS','TXS','TXXS'])
	# PipeThickness_df.set_index('nps', inplace=True)