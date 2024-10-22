"""
EXAMPLE 2
---------
Calculate  the cooling load from people for office.
"""
from pymep import Quantity
from pymep.hvac.coolingload import RTS
from pymep.hvac.internal_heat_gains import PeopleHeatGain
from pymep.hvac.people import *
from pymep.charts.chart_2D import LineChart

Q_ = Quantity

ns_rts_zone = RTS.rts_values(nrts=True, room_construction='Medium', carpet='No Carpet', glass='50%')
people_in_room = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0]
q_sen = Q_(SensibleHumanHeatRate('Seated, very light work', 'Office'), 'W')
q_lat = Q_(LatentHumanHeatRate('Seated, very light work', 'Office'), 'W')
f_rad = Q_(LowV_F_Rad('Seated, very light work', 'Office'), '%')
People_HeatGain = PeopleHeatGain('People', 
                                 ns_rts = ns_rts_zone, 
                                 usage_profile = people_in_room,
                                 Q_dot_sen_person = q_sen,
                                 Q_dot_lat_person = q_lat,
                                 F_rad = f_rad)
print('\nPeople Cooling Load')
print(People_HeatGain.update_cooling_load())

chart = LineChart(window_title = 'People Cooling Load')
x_data = [hr for hr in range(24)]
chart.add_xy_data('People',x_data,[i for i in People_HeatGain.cooling_load_df['TOTAL_CL']])
chart.x1.add_title('Local Standard Time (Hr)')
chart.y1.add_title('Load, Watt')
chart.y1.format_ticks(fmt='{x:,.0f}')
chart.add_legend(anchor='upper left', position = (0.01, 0.99))
chart.show()
