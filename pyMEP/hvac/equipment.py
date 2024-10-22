from __future__ import annotations
import pandas as pd
from abc import ABC, abstractmethod
from typing import Callable
from enum import Enum
from .. import Quantity
from .coolingload import Setting

Q_ = Quantity

eqp_df = pd.DataFrame([
    ['Training Room'            , 8.5],
    ['Meeting Room'             , 8.5],
    ['Corridor'                 , 8.5],
    ['Computer Room'            , 8.5],
    ['Laboratory'               , 8.5],
    ['Loading Dock'             , 8.5],
    ['Office'                   , 8.5],
    ['Factory'                  , 8.5],   
    ['Warehouse bulky'          , 8.5],
    ['Warehouse hand-carried'   , 8.5]],
    columns=['Space Types', 'EPD, W/m²'])

def EquipmentPowerDensities(space_type:str) -> float:
    return eqp_df[eqp_df['Space Types'].str.match(space_type)]['EPD, W/m²'].values[0]

class Equipment(ABC):

    class Category(Enum):
        MACHINE = 'machine'
        HOODED_COOKING_APPLIANCE = 'hooded_cooking_appliance'
        OFFICE_APPLIANCE = 'office_appliance'
        OFFICE_EQUIPMENT = 'office_equipment'
        GENERIC_APPLIANCE = 'generic_appliance'

    def __init__(self):
        self.ID: str = ''
        self.schedule: Callable[[float], float] | None = None
        self.F_rad: Quantity
        self.Q_dot_sen: Quantity
        self.Q_dot_sen_rd: Quantity
        self.Q_dot_sen_cv: Quantity
        self.Q_dot_lat: Quantity

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> 'Equipment':
        ...

    @abstractmethod
    def calculate_heat_gain(self, t_sol_sec: float) -> None:
        """Calculates the convective sensible, the radiative sensible and the
        latent heat gain of the equipment or appliance, but doesn't return any
        results. The results are stored in attributes `Q_dot_sen_cv` (convective
        sensible heat gain), `Q_dot_sen_rd` (radiative sensible heat gain), and
        `Q_dot_lat` (latent heat gain).
        """
        ...

class Machine(Equipment):
    """Represents any machine driven by an electric motor (e.g., a fan, a pump, etc.)."""
    class Configuration(Enum):
        MOTOR_AND_MACHINE = 'motor and machine'
        ONLY_MACHINE = 'only machine'
        ONLY_MOTOR = 'only motor'

    def __init__(self):
        super().__init__()
        self.P_motor: Quantity
        self.eta_motor: Quantity
        self.configuration: Machine.Configuration

    @classmethod
    def create( cls, ID: str,
                schedule: Callable[[float], float],
                P_motor: Quantity = Q_(0, 'W'),
                eta_motor: Quantity = Q_(0, '%'),
                configuration: Configuration = Configuration.ONLY_MACHINE,                
                F_rad: Quantity = Q_(50, '%')
    ) -> 'Machine':
        """Creates a `Machine` object.

        Parameters
        ----------
        ID:
            Identifies the machine.
        P_motor:
            Motor power nameplate rating.
        eta_motor:
            Motor efficiency.
        configuration:
            See `Enum` subclass `Configuration`:
            - `Configuration.MOTOR_AND_MACHINE`: the motor and the driven
               machine are both in the conditioned space.
            - `Configuration.ONLY_MACHINE`: only the driven machine is in the
               conditioned space.
            - `Configuration.ONLY_MOTOR`: only the motor is in the conditioned
               space (e.g. a fan in the conditioned space that exhausts air
               outside that space).
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1, where 0 stands for completely off and 1
            for running at full power.
        F_rad:
            The radiative fraction is the radiative part of the machine heat
            gain that goes to the room.
        """
        machine = cls()
        machine.ID = ID
        machine.schedule = schedule
        machine.P_motor = P_motor
        machine.eta_motor = eta_motor.to('%')
        machine.configuration = configuration        
        machine.F_rad = F_rad.to('%')
        return machine

    def calculate_heat_gain(self, t_sol_sec: float) -> None:
        if self.configuration == self.Configuration.ONLY_MACHINE:
            self.Q_dot_sen = self.P_motor
        elif self.configuration == self.Configuration.ONLY_MOTOR:
            self.Q_dot_sen = (1.0 - self.eta_motor) * (self.P_motor / self.eta_motor)
        else:
            self.Q_dot_sen = self.P_motor / self.eta_motor
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_sen *= div_fac
        self.Q_dot_sen_rd = self.F_rad * self.Q_dot_sen
        self.Q_dot_sen_cv = self.Q_dot_sen - self.Q_dot_sen_rd

class HoodedCookingAppliance(Equipment):
    """Represents a cooking appliance installed under an effective hood; only
    radiant gain adds to the cooling load of the space."""
    def __init__(self):
        super().__init__()
        self.P_rated: Quantity
        self.F_U: Quantity

    @classmethod
    def create(cls, ID: str,
               schedule: Callable[[float], float],
               P_rated: Quantity = Q_(0.0, 'W'),
               F_U: Quantity= Q_(0.0, '%'),
               F_rad: Quantity = Q_(0, '%')      
    ) -> 'HoodedCookingAppliance':
        """Creates a `HoodedCookingAppliance` object.
        (See ASHRAE Fundamentals 2017, Chapter 18, Tables 5A to 5E).

        Parameters
        ----------
        ID:
            Identifies the appliance.
        P_rated:
            Nameplate energy input rating.
        F_U:
            Usage factor applied to the nameplate rating that determines the
            average rate of appliance energy consumption.
        F_rad:
            The radiative fraction is the radiative part of the cooking
            appliance heat gain that goes to the space.
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1, where 0 stands for completely off and 1
            for running at full power.
        """
        appliance = HoodedCookingAppliance()
        appliance.ID = ID
        appliance.schedule = schedule
        appliance.P_rated = P_rated
        appliance.F_U = F_U
        appliance.F_rad = F_rad        
        return appliance

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_sen_cv = Q_(0.0, 'W')
        self.Q_dot_sen_rd = div_fac * self.F_rad * self.F_U * self.P_rated

class OfficeAppliance(Equipment):
    """Represents a single office appliance or a group of appliances in
    a room. The heat gain is calculated based on the technical specifications
    of the appliance."""
    def __init__(self):
        super().__init__()
        self.P_peak: Quantity

    @classmethod
    def create(cls, ID: str,
               schedule: Callable[[float], float],
               P_peak: Quantity = Q_(0.0, 'W'),
               F_rad: Quantity = Q_(0, '%')     
    ) -> 'OfficeAppliance':
        """Creates an `OfficeAppliance` object.

        Parameters
        ----------
        ID:
            Identifies the office appliance.
        P_peak:
            Peak heat gain.
            - Computers: see ASHRAE Fundamentals 2017, Chapter 18, Tables 8A.
              Approximately 90% convective heat gain and 10% radiative heat
              gain.
            - Laptops and laptop docking station: see ASHRAE Fundamentals 2017,
              Chapter 18, Tables 8B. Approximately 75% convective heat gain and
              25% radiative heat gain.
            - Tablet PC: see ASHRAE Fundamentals 2017, Chapter 18, Tables 8C.
            - Monitors: see ASHRAE Fundamentals 2017, Chapter 18, Table 8D.
              Approximately 60% convective heat gain and 40% radiative heat
              gain.
            - Printers and copiers: see ASHRAE Fundamentals 2017, Chapter 18,
              Table 9. Approximately 70% convective heat gain and 30% radiative
              heat gain.
            - Miscellaneous office equipment: see ASHRAE Fundamentals 2017,
              Chapter 18, Table 10.
        F_rad:
            The radiative fraction is the radiative part of the office appliance
            heat gain that goes to the space.
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1, where 0 stands for completely off and 1
            for running at full power.
        """
        appliance = OfficeAppliance()
        appliance.ID = ID
        appliance.schedule = schedule
        appliance.P_peak = P_peak        
        appliance.F_rad = F_rad
        return appliance

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_sen = div_fac * self.P_peak
        self.Q_dot_sen_rd = self.F_rad * self.Q_dot_sen
        self.Q_dot_sen_cv = self.Q_dot_sen - self.Q_dot_sen_rd

class OfficeEquipment(Equipment):
    """This class can be used to estimate the heat gain of office equipment on a
    per-square-metre basis."""
    def __init__(self):
        super().__init__()
        self.heat_density: Quantity
        self.A_floor: Quantity

    @classmethod
    def create(cls, ID: str,
               schedule: Callable[[float], float],
               heat_gain_density: Quantity = Q_(0.0, 'W / m ** 2'),
               floor_area: Quantity = Q_(0.0, 'm ** 2'),        
               F_rad: Quantity = Q_(Setting.OfficeEquipment_F_rad * 100, '%')
    ) -> 'OfficeEquipment':
        """Creates an `OfficeEquipment` object.

        Parameters
        ----------
        ID:
            Identifies the object.
        heat_gain_density:
            Heat gain per unit area, aka load factor. See ASHRAE Fundamentals
            2021, Chapter 18.14, Table 11. The medium heat gain density is likely
            to be appropriate for most standard offices.
        floor_area:
            The floor area of the space.
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1 which indicates the diversity factor.
        F_rad:
            The radiative fraction is the radiative part of the office equipment
            heat gain that goes to the space.
        """
        eqp = cls()
        eqp.ID = ID
        eqp.schedule = schedule
        eqp.heat_density = heat_gain_density.to('W / m**2')
        eqp.A_floor = floor_area.to('m**2')        
        eqp.F_rad = F_rad
        return eqp

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_sen = div_fac * self.heat_density * self.A_floor
        self.Q_dot_sen_rd = self.F_rad.to('').m * self.Q_dot_sen
        self.Q_dot_sen_cv = self.Q_dot_sen - self.Q_dot_sen_rd

class GenericAppliance(Equipment):
    """Represents a generic appliance that doesn't belong to any of the
    other categories implemented above.
    """
    def __init__(self):
        super().__init__()
        self.Q_dot_sen_pcs: Quantity
        self.Q_dot_lat_pcs: Quantity

    @classmethod
    def create(cls, ID: str,
               schedule: Callable[[float], float],
               Q_dot_sen_pcs: Quantity = Q_(0, 'W'),
               Q_dot_lat_pcs: Quantity = Q_(0, 'W'),               
               F_rad: Quantity = Q_(Setting.Equipment_Generic_F_rad * 100, '%')
    ) -> 'GenericAppliance':
        """Creates a `GenericAppliance` object of which the heat gain components
        are already known.

        Parameters
        ----------
        ID:
            Identifies the appliance.
        Q_dot_sen_rd:
            The radiative component of the sensible heat gain.
        Q_dot_sen_cv:
            The convective component of the sensible heat gain.
        Q_dot_lat:
            The latent heat gain from the appliance.
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1, where 0 stands for completely off and 1
            for running at full power.
        """
        eqp = cls()
        eqp.ID = ID
        eqp.schedule = schedule
        eqp.Q_dot_sen_pcs = Q_dot_sen_pcs
        eqp.Q_dot_lat_pcs = Q_dot_lat_pcs
        eqp.F_rad = F_rad
        return eqp

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_sen = div_fac * self.Q_dot_sen_pcs
        self.Q_dot_sen_rd = div_fac * self.F_rad.to('').m * self.Q_dot_sen_pcs
        self.Q_dot_sen_cv = self.Q_dot_sen - self.Q_dot_sen_rd
        self.Q_dot_lat = div_fac *  self.Q_dot_lat_pcs
