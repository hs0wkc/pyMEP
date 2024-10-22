import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Callable
from .. import Quantity

Q_ = Quantity

# ASHRAE Fundamentals 2021, Chapter 18, §18.5
# Table 2 Lighting Power Densities Using Space-by-Space Method
lpd_df = pd.DataFrame([
    ['Training Room'            ,'All'                                  , 13.4],
    ['Meeting Room'             ,'All'                                  , 13.3],
    ['Corridor'                 ,'In facility for visually impaired'    ,  9.9],
    ['Computer Room'            ,'All'                                  , 18.4],
    ['Laboratory'               ,'In or as classroom'                   , 15.5],
    [np.nan                     ,'All other laboratories'               , 19.5],
    ['Loading Dock'             ,'Interior'                             ,  5.1],
    ['Office'                   ,'Enclosed'                             , 12.0],
    [np.nan                     ,'Open plan'                            , 10.6],
    ['Factory'                  ,'In detailed manufacturing area'       , 13.9],
    [np.nan                     ,'In equipment room'                    ,  8.0],
    [np.nan                     ,'In extra-high-bay area 15.2m'         , 11.3],
    [np.nan                     ,'In high-bay area 7.6 to 15.2'         , 13.3],
    [np.nan                     ,'In low-bay area <7.6'                 , 12.9],
    ['Warehouse bulky'          ,'For medium to bulky, palletized items',  6.2],
    ['Warehouse hand-carried'   ,'For smaller, hand-carried items'      , 10.2]],
    columns=['Space Types', 'Category', 'LPD, W/m²'])
lpd_df.ffill(inplace=True)

def LightingPowerDensities(space_type:str, category:str|None = None) -> float:
    # print(lpd_df[lpd_df['Space Types'].str.match('Office') & lpd_df.Category.str.match('Enclosed')])
    # print(lpd_df[lpd_df['Space Types'].str.match('Office') & lpd_df.Category.str.match('Enclosed')]['LPD, W/m²'])
    # Column Name have space must be used ['__'] and not used '(' or ')'
    if category is not None:
        return lpd_df[lpd_df['Space Types'].str.match(space_type) & lpd_df.Category.str.match(category)]['LPD, W/m²'].values[0]
    else:
        return lpd_df[lpd_df['Space Types'].str.match(space_type)]['LPD, W/m²'].values[0]

class Lighting(ABC):

    def __init__(self):
        self.ID: str = ''
        self.schedule: Callable[[float], float] | None = None
        self.F_space: Quantity
        self.F_rad: Quantity
        self.Q_dot_light: Quantity

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> 'Lighting':
        ...

    @abstractmethod
    def calculate_heat_gain(self, t_sol_sec: float) -> None:
        ...

class LightingFixture(Lighting):
    """Represents a single lighting fixture or a group of lighting fixtures in
    a room. The light heat gain is calculated based on the lighting fixture's
    technical specifications.
    """
    def __init__(self):
        super().__init__()
        self.P_lamp: Quantity
        self.F_allowance: Quantity
        self.F_use : Quantity

    @classmethod
    def create( cls, ID: str,
                schedule: Callable[[float], float],
                P_lamp: Quantity = Q_(0.0, 'W'),
                F_allowance: Quantity= Q_(0.0, '%'),
                F_rad: Quantity = Q_(0.58,'').to('%'),
                F_use : Quantity = Q_(1.0,'').to('%')
    ) -> 'LightingFixture':
        """Creates a `LightingFixture` object.
        (see ASHRAE Fundamentals 20121, Chapter 18, 2.2 Lighting).

        Parameters
        ----------
        ID:
            Identifies the lighting fixture.
        P_lamp:
            The nominal wattage of the lamp(s) in the fixture without the power
            consumption of ballasts.
        F_allowance:
            The ratio of the lighting fixture's power consumption including
            lamps and ballast to the nominal power consumption of the lamps.
            For incandescent lamps, this factor is 1. For fluorescent and other
            lights, it accounts for power consumed by the ballast as well as the
            ballast's effect on lamp power consumption.
        schedule:
            Function with signature `f(t_sol_sec: float) -> bool` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1, where 0 stands for completely turned off
            and 1 for maximum lighting power.
        F_use:
            The ratio of the lamp wattage in use to the total installed wattage
            for the conditions under which the cooling load estimate is being
            made. For commercial applications such as stores, the use factor is
            usually 1.0.

        Notes
        -----
        A single `LightingFixture` object could also be used to represent a
        group of multiple lighting fixtures instead of only a single fixture.
        """
        fixture = cls()
        fixture.ID = ID
        fixture.schedule = schedule
        fixture.P_lamp = P_lamp
        fixture.F_allowance = F_allowance
        fixture.F_use = F_use
        fixture.F_rad = F_rad
        return fixture

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_light = div_fac * self.P_lamp * self.F_use.to('').m * self.F_allowance.to('').m

class SpaceLighting(Lighting):
    """This class can be used to estimate the lighting gain on a
    per-square-metre basis (e.g., when final lighting plans are not available).
    """
    def __init__(self):
        super().__init__()
        self.power_density: Quantity
        self.A_floor: Quantity

    @classmethod
    def create( cls, ID: str,
                schedule: Callable[[float], float],
                power_density: Quantity = Q_(0.0,'W / m ** 2'),
                floor_area: Quantity = Q_(0.0, 'm ** 2'),
                F_rad: Quantity = Q_(0.58,'').to('%'),
                F_space: Quantity = Q_(0.69,'').to('%')
    ) -> 'SpaceLighting':
        """Creates a `SpaceLighting` object.
        (see c).

        Parameters
        ----------
        ID:
            Identifies the space lighting.
        power_density:
            The maximum lighting power density, i.e. the lighting heat gain per
            square metre (see ASHRAE Fundamentals 2017, Chapter 18, Table 2).
        floor_area
            The floor area of the zone.
        schedule:
            Function with signature `f(t_sol_sec: float) -> float` that takes the
            solar time `t_sol_sec` in seconds from midnight (0 s) and returns
            a float between 0 and 1 which indicates the diversity factor.
        F_rad:
            The radiative fraction is the radiative part of the lighting heat
            gain that goes to the room (see ASHRAE Fundamentals 2017, Chapter
            18, Table 3 and Figure 3).
        F_space:
            The space fraction, i.e., the fraction of lighting heat gain that
            goes to the room (the other fraction goes to the plenum) (see ASHRAE
            Fundamentals 2017, Chapter 18, Table 3 and Figure 3).
        """
        lighting = cls()
        lighting.ID = ID
        lighting.schedule = schedule
        lighting.power_density = power_density
        lighting.A_floor = floor_area
        lighting.F_space = F_space
        lighting.F_rad = F_rad
        return lighting

    def calculate_heat_gain(self, t_sol_sec: float):
        div_fac = self.schedule(t_sol_sec)
        self.Q_dot_light = div_fac * self.F_space.to('').m * self.power_density * self.A_floor
