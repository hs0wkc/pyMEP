import numpy as np
from enum import Enum
from CoolProp.HumidAirProp import HAPropsSI
from scipy.optimize import fsolve
from scipy.constants import Stefan_Boltzmann

import pyMEP.HeatTransfer.NaturalConvection.ExternalFlow.horizontal_cylinder as hCylinder
import pyMEP.HeatTransfer.NaturalConvection.ExternalFlow.vertical_cylinder as vCylinder
import pyMEP.HeatTransfer.NaturalConvection.ExternalFlow.vertical_plate as vPlate
import pyMEP.HeatTransfer.NaturalConvection.ExternalFlow.horizontal_plate as hPlate
from ..substance import Fluid, FluidState, INSULATION
from pyMEP import Quantity

Q_ = Quantity

class Insulation:

	class SurfaceType(Enum):
		Horizontal_Cylinder = 0
		Vertical_Cylinder = 1
		Horizontal_Plate = 2
		Vertical_Plate = 3	
		Sphere = 4

	_pressure = 101325	
	_t_amb : Quantity
	_t_rh : Quantity 
	_t_inside : Quantity 
	_dew_point : Quantity	
	_t_flm : Quantity
	_Air : FluidState = Fluid('Air')	
	_air : FluidState
	configuration : tuple = ('upwards-heated','downwards-cooled','downwards-heated','upwards-cooled')

	def __init__(self,
			  t_amb:Quantity, 
			  t_rh:Quantity=Q_(50,'%'), 
			  t_inside:Quantity=Q_(280.15, 'degK'), 
			  insulation:str='MicroFiber', 
			  emissivity:float|None=None):		
		self._t_amb = t_amb.to('degK')
		self._t_rh = t_rh
		self._t_inside = t_inside.to('degK')
		self.insulation = insulation
		self.surface_Emissivity = emissivity
		self.FluidState_Change()

	def FluidState_Change(self):
		self._dew_point = Q_(HAPropsSI('D','T',self.t_amb.m,'P',self._pressure,'R',self.t_rh.to('').m),'degK')
		self._t_flm = (self.t_amb + self._dew_point) / 2
		self._air = self._Air(T=self._t_flm, P=Q_(self._pressure, 'Pa'))
		mean_temperature = (self.t_inside + self._t_flm)/2
		self.k = INSULATION.ThermalConductivity(self.insulation, mean_temperature.to('degC').m)
		if self.surface_Emissivity is None:
			self.surface_Emissivity = INSULATION._property_table[self.insulation].Emissivity
		self.hr = self.surface_Emissivity * Q_(Stefan_Boltzmann,'watt* m**-2 * K**-4') * (self.t_amb ** 4 - self._dew_point **4)/(self.t_amb - self._dew_point)

	def CondensateInsulationThickness_Cylinder(self, surface_type:SurfaceType, od:Quantity)->Quantity|None:

		# Define the function to solve
		def fsolve_thickness(t, d1):
			global hs
			return (d1 + 2*t) * np.log(1 + 2*t/d1) - (2*self.k / hs) * (self._dew_point.m - self.t_inside.m) / (self.t_amb.m - self._dew_point.m)

		def recursive_diameter(d1):
			global hs
			cylinder.D = Q_(d1, 'm')
			hc = cylinder.avg_heat_trf_coeff()
			hs  = hc.m + self.hr.m
			t_solution = fsolve(fsolve_thickness, 1, d1)
			new_od = pipe_od + 2*t_solution
			if np.round(d1,2) == np.round(new_od,2):
				return d1
			else:		
				return recursive_diameter(new_od)

		match surface_type:
			case self.SurfaceType.Horizontal_Cylinder:
				cylinder = hCylinder.Cylinder(D=od, L=Q_(1, 'm'), T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case self.SurfaceType.Vertical_Cylinder:
				cylinder = vCylinder.Cylinder(D=od, L=Q_(1, 'm'), T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case _:
				return None
		pipe_od = od.to('m').m
		dx = recursive_diameter(pipe_od)
		cylinder.D = Q_(dx,'m')
		self.hc = cylinder.avg_heat_trf_coeff()
		hs  = self.hc.m + self.hr.m
		t_solution = fsolve(fsolve_thickness, 1, dx)
		self.Surface = cylinder
		return Q_(t_solution[0],'m').to('mm')

	def CondensateInsulationThickness_Plate(self, 
										 surface_type:SurfaceType, 
										 l:Quantity = Q_(1, 'm'), 
										 w:Quantity|None=None, 
										 config: str = configuration[1]) -> Quantity|None:
		match surface_type:
			case self.SurfaceType.Horizontal_Plate:
				plate = hPlate.Plate(L=l, W=w, T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air, configuration=config)
			case self.SurfaceType.Vertical_Plate:
				plate = vPlate.Plate(L=l, T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case _:
				return None
		self.hc = plate.avg_heat_trf_coeff()
		hs  = self.hc.m + self.hr.m
		t_solution = (self.k/hs)*((self._dew_point - self.t_inside)/(self.t_amb - self._dew_point))
		self.Surface = plate
		return Q_(t_solution.m,'m').to('mm')

	def ThermalInsulationThickness_Cylinder(self, surface_type:SurfaceType, od:Quantity, thk:Quantity)->Quantity|None:

		def SurfaceTemperature(t_surf):		
			global q
			cylinder.T_surf = t_surf
			self.hc = cylinder.avg_heat_trf_coeff()
			self.hr = self.surface_Emissivity * Q_(Stefan_Boltzmann,'watt* m**-2 * K**-4') * (t_surf ** 4 - self.t_amb **4)/(t_surf - self.t_amb)
			hs = self.hc.m + self.hr.m
			A = np.log(total_od/pipe_od)/(2*np.pi*self.k)
			B = 1/(np.pi*total_od*hs)
			q = (mean_temperature - self.t_amb)/(A.m+B.m)
			t = q.m/(np.pi*pipe_od.m*hs) + self.t_amb.m
			return t
		
		def recursive_temperature(t):
			new_t = SurfaceTemperature(Q_(t, 'degK'))
			if np.round(t,2) == np.round(new_t,2):
				return t
			else:		
				return recursive_temperature(new_t)

		pipe_od = od.to('m')
		total_od = pipe_od + 2*thk.to('m')		
		match surface_type:
			case self.SurfaceType.Horizontal_Cylinder:
				cylinder = hCylinder.Cylinder(D=total_od, L=Q_(1, 'm'), T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case self.SurfaceType.Vertical_Cylinder:
				cylinder = vCylinder.Cylinder(D=total_od, L=Q_(1, 'm'), T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case _:
				return None
		mean_temperature = (self.t_amb + self.t_inside)/2
		self.k = INSULATION.ThermalConductivity(self.insulation, mean_temperature.to('degC').m)
		t = recursive_temperature(mean_temperature)
		self.Surface = cylinder
		return Q_(t, 'degK').to('degC'), Q_(q.m, 'W/m')

	def ThermalInsulationThickness_Plate(self, 
									  surface_type:SurfaceType, 
									  thk:Quantity, 
									  l:Quantity = Q_(1, 'm'), 
									  w:Quantity|None=None, 
									  config: str = configuration[0]) -> Quantity|None:

		def SurfaceThickness(t_surf):
			global hs
			plate.T_surf = t_surf
			self.hc = plate.avg_heat_trf_coeff()
			self.hr = self.surface_Emissivity * Q_(Stefan_Boltzmann,'watt* m**-2 * K**-4') * (t_surf ** 4 - self.t_amb **4)/(t_surf - self.t_amb)
			hs = self.hc.m + self.hr.m
			thk = (self.k/hs)*((t_surf - self.t_inside)/(self.t_amb - t_surf))
			return thk

		match surface_type:
			case self.SurfaceType.Horizontal_Plate:
				plate = hPlate.Plate(L=l, W=w, T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air, configuration=config)
			case self.SurfaceType.Vertical_Plate:
				plate = vPlate.Plate(L=l, T_surf=self.t_amb, T_inf=self._dew_point, fluid=self._air)
			case _:
				return None
		mean_temperature = (self.t_amb + self.t_inside)/2
		self.k = INSULATION.ThermalConductivity(self.insulation, mean_temperature.to('degC').m)
		t = self.t_inside
		while t > self.t_amb:			
			thickness = SurfaceThickness(t)
			if thickness.m >= Q_(thk,'m').m:
				break
			# print(t.to('degC') ,Q_(thickness.m,'m').to('mm'))
			t -= Q_(0.5,'degK')
		self.Surface = plate
		return Q_(t.m + 0.5, 'degK').to('degC'), Q_(hs*(t.m - self.t_amb.m), 'W/m ** 2')

	@property
	def t_amb(self) -> Quantity:
		return self._t_amb
	@t_amb.setter
	def t_amb(self, v: Quantity) -> None:
		self._t_amb = v.to('degK')
		self.FluidState_Change()

	@property
	def t_rh(self) -> Quantity:
		return self._t_rh
	@t_rh.setter
	def t_rh(self, v: Quantity) -> None:
		self._t_rh = v
		self.FluidState_Change()

	@property
	def t_inside(self) -> Quantity:
		return self._t_inside
	@t_inside.setter
	def t_inside(self, v: Quantity) -> None:
		self._t_inside = v.to('degK')
		self.FluidState_Change()
		
