"""
EXAMPLE 4
---------
Calculate the cooling load contribution from the Operable Single Clear Glass 6mm window 
of wall section facing 60° west of south.
"""
from pymep import Quantity
from pymep.hvac.climatic import WeatherData, ReferenceDates
from pymep.hvac.coolingload import RTS
from pymep.hvac.external_heat_gains import *
from pymep.charts.chart_2D import LineChart

Q_ = Quantity

weather_data_01 = WeatherData.create_from_climatic_design_data(
    ID='Atlanta USA',
    fi = Q_(33.640, 'deg'), 
    L_loc = Q_(-84.4, 'deg'), 
    altitude = Q_(313, 'feet').to('m'), 
    date = ReferenceDates.get_date_for('jul'),
    T_db_des = Q_(33.1, 'degC'),
    T_db_rng = Q_(9.3, 'delta_degC'),
    T_wb_mc = Q_(23.2, 'degC'),
    T_wb_rng = Q_(3.4, 'delta_degC'),
    taub = 0.515, 
    taud = 2.066,
    tz=-5
)
area = Q_(5.57, 'm ** 2')
ns_rts_zone = RTS.rts_values(nrts=True, room_construction='Medium', carpet='With Carpet', glass='50%')
s_rts_zone = RTS.rts_values(nrts=False, room_construction = 'Medium', carpet = 'With Carpet', glass = '50%')

print(f'{weather_data_01.ID} Sun Position')
print(weather_data_01.update_sun_position())

w1_cts = [18,57,20,4,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
w1 = Wall.creat_external_wall('Wall_1',
                              weather_data = weather_data_01, 
                              surface_azimuth = Q_(60, 'deg'),
                              gross_area = area,
                              U = Q_(0.44, 'W / (m**2 * K)'),
                              CTS = w1_cts,
                              NS_RTS = ns_rts_zone)
w1.add_window(id='Win-A', width=Q_(1.5, 'm'), height=Q_(1.0, 'm'), U=Q_(3.18, 'W / (m**2 * K)').m, SC=0.9)
win = w1.windows.get('Win-A')
win.SHGCd = [0.81, 0.80, 0.78, 0.73, 0.62, 0.39, 0]
win.SHGCh = 0.73
win.S_RTS = s_rts_zone

w1.update_cooling_load()
print(f'{w1.ID} Solar Irradiance')
print(w1.solar_irradiance_df)
print(f'{w1.ID} Cooling Load')
print(w1.cooling_load_df)
print(f'{win.ID} Cooling Load')
print(win.update_cooling_load())

chart = LineChart(window_title = 'Wall & Window Cooling Load')
x_data = [hr for hr in range(24)]
chart.add_xy_data('Wall',x_data,[i for i in w1.cooling_load_df['TOTAL_CL']])
chart.add_xy_data('Window',x_data,[i for i in win.cooling_load_df['TOTAL_CL']])
chart.x1.add_title('Local Standard Time (Hr)')
chart.y1.add_title('Load, Watt')
chart.y1.format_ticks(fmt='{x:,.0f}')
chart.add_legend(anchor='upper left', position = (0.01, 0.99))
chart.show()

