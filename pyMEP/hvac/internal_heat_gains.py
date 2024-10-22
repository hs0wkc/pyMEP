from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from .. import Quantity
from .equipment import Equipment
from .lighting import Lighting
from .people import People
from .coolingload import TimeSeriesMethod

Q_ = Quantity

class InternalHeatGain(ABC):

    def __init__(self, ID: str, ns_rts: pd.DataFrame | None, usage_profile: list| None):
        self.ID = ID
        # Default Profile - Operation is from 8:00 to 17:00.
        self.usage_profile =  usage_profile if usage_profile is not None else [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0]
        self.cooling_load_df = pd.DataFrame(self.usage_profile, columns=['UPro'])
        self.cooling_load_df['NS-RTS'] = ns_rts if ns_rts is not None else [100,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        
    @abstractmethod
    def Q_dot(self, t_sol_sec: float) -> tuple[float, float, float]:
        """Returns a 3-tuple with the convective sensible, the radiative
        sensible, and the latent internal heat gain in Watts at solar time
        `t_sol_sec` in seconds from 00:00:00.
        """
        ...

    @abstractmethod
    def update_cooling_load(self) -> pd.DataFrame:
        """Update Cooling Load Component DataFrame as current component.
        """
        ...

    def usage_schedule(self, t_sol_sec: float) -> float:
        return self.usage_profile[int(t_sol_sec/3600)]

    def UpdateUsageProfile(self, usage_profile: list) -> None:
        self.usage_profile = usage_profile
        self.cooling_load_df['UPro'] = usage_profile
        
    def Update_ns_rts(self, ns_rts: pd.DataFrame) -> None:
        self.cooling_load_df['NS-RTS'] = ns_rts
        self.update_cooling_load()

class EquipmentHeatGain(InternalHeatGain):
    """Represents the internal heat gain from equipment in the space.
    An `EquipmentHeatGain` object contains one or more `Equipment` objects
    (see module equipment.py). The user must create these objects with the
    necessary input data so that the heat gain of this equipment can be
    calculated."""
    def __init__(self, ID: str, ns_rts: pd.DataFrame | None = None, usage_profile: list | None = None):
        super().__init__(ID, ns_rts, usage_profile)
        self.equipment: dict[str, Equipment] = {}

    def add_equipment(self, eqp: Equipment):
        """Adds an `Equipment` object (any object of subclass `Machine`,
        `HoodedCookingAppliance`, `OfficeAppliance`, `OfficeEquipment` or
        `GenericAppliance) to this `EquipmentHeatGain` object."""
        self.equipment[eqp.ID] = eqp

    def remove_equipment(self, eqp_ID: str):
        """Removes the equipment with ID `eqp_ID` from this `EquipmentHeatGain` object."""
        self.equipment.pop(eqp_ID)

    def get_equipment(self, eqp_ID: str) -> Equipment:
        """Returns the equipment with ID `eqp_ID`."""
        return self.equipment[eqp_ID]
        # return self.equipment.get(eqp_ID)

    def Q_dot(self, t_sol_sec: float) -> tuple[float, float, float, float]:
        Q_dot_sen = 0.0
        Q_dot_sen_rd = 0.0
        Q_dot_sen_cv = 0.0
        Q_dot_lat = 0.0
        for eqp in self.equipment.values():
            eqp.calculate_heat_gain(t_sol_sec)
            Q_dot_sen += eqp.Q_dot_sen.to('W').m
            Q_dot_sen_rd += eqp.Q_dot_sen_rd.to('W').m
            Q_dot_sen_cv += eqp.Q_dot_sen_cv.to('W').m
            Q_dot_lat += eqp.Q_dot_lat.to('W').m
        return Q_dot_sen, Q_dot_sen_rd, Q_dot_sen_cv, Q_dot_lat 

    def update_cooling_load(self):
        Q_dot_sen, Q_dot_sen_rd, Q_dot_sen_cv, Q_dot_lat = [],[],[],[]
        for i in range(24):
            Q = self.Q_dot(i * 3600)
            Q_dot_sen.append(Q[0])
            Q_dot_sen_rd.append(Q[1])
            Q_dot_sen_cv.append(Q[2])            
            Q_dot_lat.append(Q[3])
        self.cooling_load_df['SenHG'] = Q_dot_sen
        self.cooling_load_df['SenToRad'] = Q_dot_sen_rd
        self.cooling_load_df['SenToCon'] = Q_dot_sen_cv
        self.cooling_load_df['LatHG'] = Q_dot_lat
        rts_cooling_load = TimeSeriesMethod(ts = self.cooling_load_df['NS-RTS'].tolist(), 
                                            heat_load = Q_dot_sen_rd,
                                            id = self.ID, tstype='NS-RTS')
        rts_cooling_load.columns = ['RTS_CL']
        self.cooling_load_df['RTS_CL'] = rts_cooling_load
        Total_Cooling_Load = self.cooling_load_df['LatHG'] + self.cooling_load_df['SenToCon'] + rts_cooling_load
        Total_Cooling_Load.columns = ['TOTAL_CL']
        self.cooling_load_df['TOTAL_CL'] = Total_Cooling_Load
        return self.cooling_load_df

class LightingHeatGain(InternalHeatGain):
    """Represents the internal heat gain from space lighting.
    A `LightingHeatGain` object contains one or more `Lighting` objects
    (see module lighting.py). The user must create these objects with the
    necessary input data so that the heat gain of the lighting can be
    calculated."""
    def __init__(self, ID: str, ns_rts: pd.DataFrame | None = None , usage_profile: list | None = None):
        super().__init__(ID, ns_rts, usage_profile)
        self.lighting: dict[str, Lighting] = {}        

    def add_lighting(self, light: Lighting):
        """Adds a `Lighting` object (object of class `LightingFixture` or class
        `SpaceLighting`) to this `LightingHeatGain` object.
        """
        self.lighting[light.ID] = light

    def remove_lighting(self, ID: str):
        """Removes the `Lighting` object with given ID from this
        `LightingHeatGain` object."""
        self.lighting.pop(ID)

    def get_lighting(self, ID: str) -> Lighting:
        """Returns the `Lighting` object with given ID."""
        return self.lighting[ID]

    def Q_dot(self, t_sol_sec: float) -> tuple[float, float, float]:
        Q_dot_sen_rd = 0.0
        Q_dot_sen_cv = 0.0
        for light in self.lighting.values():
            light.calculate_heat_gain(t_sol_sec)
            Q_dot_light = light.Q_dot_light.to('W').m
            Q_dot_sen_rd += light.F_rad.to('').m * Q_dot_light
            Q_dot_sen_cv += (1 - light.F_rad.to('').m) * Q_dot_light
        return Q_dot_sen_cv, Q_dot_sen_rd, 0.0

    def update_cooling_load(self):
        Q_total,Q_con,Q_rad = [],[],[]
        for i in range(24):
            Q = self.Q_dot(i * 3600)            
            Q_con.append(Q[0])
            Q_rad.append(Q[1])
            Q_total.append(Q[0]+Q[1])
        self.cooling_load_df['TotalHG'] = Q_total
        self.cooling_load_df['ConHG'] = Q_con
        self.cooling_load_df['RadHG'] = Q_rad
        rts_cooling_load = TimeSeriesMethod(ts = self.cooling_load_df['NS-RTS'].tolist(), 
                                            heat_load = Q_rad,
                                            id = self.ID, tstype='NS-RTS')
        rts_cooling_load.columns = ['RTS_CL']
        self.cooling_load_df['RTS_CL'] = rts_cooling_load

        Total_Cooling_Load = self.cooling_load_df['ConHG'] + rts_cooling_load
        Total_Cooling_Load.columns = ['TOTAL_CL']
        self.cooling_load_df['TOTAL_CL'] = Total_Cooling_Load
        return self.cooling_load_df

class PeopleHeatGain(InternalHeatGain):
    """Represents the heat gain from people in the space."""
    def __init__(self, 
                 ID: str, 
                 ns_rts: pd.DataFrame | None = None, 
                 usage_profile: list | None = None,
                 Q_dot_sen_person: Quantity = Q_(70, 'W'), 
                 Q_dot_lat_person: Quantity = Q_(45, 'W'), 
                 F_rad: Quantity = Q_(60, '%')):
        super().__init__(ID, ns_rts, usage_profile)
        self.occupants = People.create(ID='Occupants', 
                                       Q_dot_sen_person=Q_dot_sen_person, 
                                       Q_dot_lat_person=Q_dot_lat_person, 
                                       F_rad=F_rad, 
                                       schedule=self.usage_schedule)

    def Q_dot(self, t_sol_sec: float) -> tuple[float, float, float, float]:
        return self.occupants.calculate_heat_gain(t_sol_sec)

    def update_cooling_load(self):
        Q_dot_sen, Q_dot_sen_rd, Q_dot_sen_cv, Q_dot_lat = [],[],[],[]
        for i in range(24):
            Q = self.Q_dot(i * 3600)
            Q_dot_sen.append(Q[0])
            Q_dot_sen_rd.append(Q[1])
            Q_dot_sen_cv.append(Q[2])            
            Q_dot_lat.append(Q[3])
        self.cooling_load_df['SenHG'] = Q_dot_sen
        self.cooling_load_df['SenToRad'] = Q_dot_sen_rd
        self.cooling_load_df['SenToCon'] = Q_dot_sen_cv
        self.cooling_load_df['LatHG'] = Q_dot_lat
        rts_cooling_load = TimeSeriesMethod(ts = self.cooling_load_df['NS-RTS'].tolist(), 
                                            heat_load = Q_dot_sen_rd,
                                            id = self.ID, tstype='NS-RTS')
        rts_cooling_load.columns = ['RTS_CL']
        self.cooling_load_df['RTS_CL'] = rts_cooling_load
        Total_Cooling_Load = self.cooling_load_df['LatHG'] + self.cooling_load_df['SenToCon'] + rts_cooling_load
        Total_Cooling_Load.columns = ['TOTAL_CL']
        self.cooling_load_df['TOTAL_CL'] = Total_Cooling_Load
        return self.cooling_load_df
