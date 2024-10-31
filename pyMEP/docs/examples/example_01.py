"""
EXAMPLE 1
---------
Calculate  the cooling load from lighting for office.
"""
from pyMEP import Quantity
from pyMEP.hvac.coolingload import RTS
from pyMEP.hvac.internal_heat_gains import LightingHeatGain
from pyMEP.hvac.lighting import *
from pyMEP.charts.chart_2D import LineChart

Q_ = Quantity

area = Q_(12, 'm ** 2')
ns_rts_zone = RTS.rts_values(nrts=True, room_construction='Medium', carpet='With Carpet', glass='50%')
Light_HeatGain = LightingHeatGain(ID="Lighting", ns_rts = ns_rts_zone)
lpd = Q_(LightingPowerDensities(space_type='Office', category='Enclosed'), 'W / m ** 2')
ls0 = SpaceLighting.create(ID="ls0", power_density=lpd, floor_area=area, schedule=Light_HeatGain.usage_schedule)
lf0 = LightingFixture.create(ID = "lf1", P_lamp = Q_(110, 'W'), F_allowance = Q_(85, '%'), schedule = Light_HeatGain.usage_schedule)

Light_HeatGain.add_lighting(ls0)
Light_HeatGain.add_lighting(lf0)
print('\nLighting Cooling Load')
print(Light_HeatGain.update_cooling_load())

chart = LineChart(window_title = 'Lighting Cooling Load')
x_data = [hr for hr in range(24)]
chart.add_xy_data('Lighting',x_data,[i for i in Light_HeatGain.cooling_load_df['TOTAL_CL']])
chart.x1.add_title('Local Standard Time (Hr)')
chart.y1.add_title('Load, Watt')
chart.y1.format_ticks(fmt='{x:,.0f}')
chart.add_legend(anchor='upper left', position = (0.01, 0.99))
chart.show()
