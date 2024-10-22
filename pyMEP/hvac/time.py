"""Copyright (c) 2023 Tom Christiaens
https://github.com/TomLXXVI/python-hvac
"""
import numpy as np
import numpy.typing as npt
import pytz
from datetime import time as Time
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta
from .. import Quantity

def time_to_decimal_hour(time: Time) -> float:
    """Converts time into decimal hours."""
    milliseconds = time.hour * 3.6e6
    milliseconds += time.minute * 6.0e4
    milliseconds += time.second * 1.0e3
    milliseconds += time.microsecond / 1.0e3
    hour = milliseconds / 3.6e6
    return hour

def decimal_hour_to_time(t_hr: npt.ArrayLike) -> Time:
    """Converts decimal hour into time."""
    milliseconds = t_hr * 3.6e6
    hours = milliseconds // 3.6e6
    milliseconds %= 3.6e6
    minutes = milliseconds // 6e4
    milliseconds %= 6e4
    seconds = milliseconds // 1e3
    milliseconds %= 1e3
    return Time(int(hours), int(minutes), int(seconds), int(milliseconds * 1e3))

def day_number(date: Date) -> int:
    """Returns the number of the day of the year of a given date."""
    time_delta = date - Date(date.year, 1, 1)

    return time_delta.days + 1

def day_number_to_date(n: int, year: int = 2023) -> Date:
    """Convert day number `n` to a Python date object."""
    date = Date(year, 1, 1) + timedelta(days=n - 1)
    return date

def hour_angle_to_solar_time(omega: npt.ArrayLike) -> npt.ArrayLike:
    """Returns solar time in decimal hours, given hour angle `omega` in radians.
    """
    t_sol = np.degrees(omega) / 15 + 12
    return t_sol

def _time_correction(dt_clock: DateTime, L_loc: float, n: int) -> float:
    """The time correction factor in minutes accounts for the variation of
    the local solar time within a given time zone due to the longitude
    variations within the time zone and also incorporates the equation of time,
    an empirical equation that corrects for the eccentricity of the Earth's orbit
    and the Earth's axial tilt.
    ASHRAE Handbook-Fundamentals 2021 p14.8, Equation of Time and Solar Time.
    """
    if L_loc > 0.0:
        L_loc = 360.0 - L_loc   # east of Greenwich
    else:        
        L_loc = abs(L_loc)      # Greenwich or west of Greenwich

    utc_offset = dt_clock.utcoffset().total_seconds() / 3600.0
    L_st = 15.0 * utc_offset
    if L_st > 0.0:
        L_st = 360.0 - L_st     # east of Greenwich
    else:        
        L_st = abs(L_st)        # Greenwich or west of Greenwich

    B = np.radians((n - 1) * 360 / 365)
    E = (229.2 * (7.5e-5 + 1.868e-3 * np.cos(B) - 0.032077 * np.sin(B)
        - 0.014615 * np.cos(2 * B) - 0.04089 * np.sin(2 * B)))
    tc = 4.0 * (L_st - L_loc) + E
    return tc

def clock_to_solar_time(dt_clock: DateTime, L_loc: float) -> DateTime:
    """Convert a time-zone aware local standard date-time `dt_clock` at longitude
    `L_loc` to solar date-time. Longitude `L_loc` in decimal degrees must be
    positive east of Greenwich and negative west of Greenwich.

    Notes
    -----
    To create a time-zone aware date-time object, we can use the package `pytz`.
    ```
    tz = pytz.timezone('Europe/Brussels')
    dt_naive = datetime(2023, 7, 17, 12, 0, 0)  # July 17 2023 12:00
    dt_std = tz.localize(dt_naive)
    ```
    """
    n = day_number(dt_clock.date())
    tc = _time_correction(dt_clock, L_loc, n)
    t_std = time_to_decimal_hour(dt_clock.time())
    t_solar = t_std + tc / 60.0
    if t_solar < 0.0:
        t_solar += 24.0
        n -= 1
    if t_solar >= 24.0:
        t_solar -= 24.0
        n += 1
    dt_solar = DateTime.combine(
        day_number_to_date(n, year=dt_clock.year),
        decimal_hour_to_time(t_solar),
        tzinfo=dt_clock.tzinfo
    )
    return dt_solar

def solar_to_clock_time(dt_solar: DateTime, L_loc: float) -> DateTime:
    """Convert time-zone aware solar date-time `dt_solar` at longitude `L_loc`
    to local standard date-time. Longitude `L_loc` is in degrees and must be
    positive east of UTC and negative west of UTC.
    """
    n = day_number(dt_solar.date())
    tc = _time_correction(dt_solar, L_loc, n)
    t_solar = time_to_decimal_hour(dt_solar.time())
    t_std = t_solar - tc / 60.0
    if t_std < 0.0:
        t_std += 24.0
        n -= 1
    if t_std >= 24.0:
        t_std -= 24.0
        n += 1
    dt_local = DateTime.combine(
        day_number_to_date(n, year=dt_solar.year),
        decimal_hour_to_time(t_std),
        tzinfo=dt_solar.tzinfo
    )
    return dt_local

def convert_to_clock_time(
    time_index: int,
    dt_hr: float,
    date: Date,
    L_loc: Quantity,
    tz_loc: str
) -> tuple[DateTime, DateTime]:
    """Converts a time index with given time step in local solar time and also
    to local standard time.

    Parameters
    ----------
    time_index:
        Time index indicating a moment in time of the day.
    dt_hr:
        The time step in decimal hours used to perform the dynamic heat transfer
        calculations of exterior building elements.
    date:
        The date of the day under consideration.
    L_loc:
        The longitude of the location under consideration. East from Greenwich
        is a positive angle, and west is a negative angle.
    tz_loc:
        The time zone of the location conform the tz database notation.

    Returns
    -------
    A 2-tuple with:
    -   Python datetime object representing the date and local standard time that
        corresponds with the given time index and time step.
    -   Python datetime object representing the date and local solar time that
        corresponds with the given time index and time step.
    """
    t_sol_hr_dec = time_index * dt_hr
    sol_time = decimal_hour_to_time(t_sol_hr_dec)
    sol_datetime = DateTime.combine(date, sol_time)     # naive date-time
    tz_loc = pytz.timezone(tz_loc)
    sol_datetime = tz_loc.localize(sol_datetime)        # timezone aware date-time
    std_datetime = solar_to_clock_time(sol_datetime, L_loc.to('deg').m)
    return std_datetime, sol_datetime

def convert_to_solar_seconds(
    clock_time: Time,
    date: Date,
    L_loc: Quantity,
    tz_loc: str
) -> float:
    """Converts a clock time (a local standard time) in a given time zone on a
    given date to solar time in seconds from midnight (0 s).

    Parameters
    ----------
    clock_time:
        The clock time being read.
    date:
        The date at which the clock time is being read.
    L_loc:
        The longitude where the clock time is being read. East of Greenwich is
        a positive angle, west of greenwich is a negative angle.
    tz_loc:
        The timezone in which the clock time is being read conform the tz
        database notation.

    Returns
    -------
    A float, being the solar time in seconds from midnight (0 s)
    """
    dt_clock = DateTime.combine(
        date=date,
        time=clock_time
    )
    tz_loc = pytz.timezone(tz_loc)
    dt_clock = tz_loc.localize(dt_clock)
    dt_sol = clock_to_solar_time(dt_clock, L_loc.to('deg').m)
    t_sol = dt_sol.time()
    t_sol_sec = time_to_decimal_hour(t_sol) * 3600
    return t_sol_sec

def equation_of_time(n: float | np.ndarray) -> float | np.ndarray:
    """The earth’s orbital velocity also varies throughout the year, so
    apparent solar time (AST), as determined by a solar time sundial,
    varies somewhat from the mean time kept by a clock running at a
    uniform rate. This variation is called the equation of time (ET) and
    is approximated by the following formula
    ASHRAE Fundamentals 2021 p14.8 Equation of Time and Solar Time

    n : day of the year
    """
    B = np.radians((n - 1) * 360 / 365)
    # E = (229.2 * (7.5e-5 + 1.868e-3 * np.cos(B) - 0.032077 * np.sin(B) - 0.014615 * np.cos(2 * B) - 0.04089 * np.sin(2 * B)))
    E = (2.2918 * (0.0075 + 0.1868*np.cos(B) - 3.2077*np.sin(B) - 1.4615*np.cos(2*B) - 4.089*np.sin(2*B)))
    return E

def apparent_solar_time(LST: float | np.ndarray, n: float | np.ndarray, LON:Quantity, TZ:int) -> float | np.ndarray:
    """AST : Apparent Solar Time
    The  conversion  between  local  standard  time  and  solar  time
    involves two steps: the equation of time is added to the local standard time, 
    and then a longitude correction is added. This longitude
    correction is four minutes of time per degree difference between the
    local  (site)  longitude  and  the  longitude  of  the  local  standard
    meridian (LSM) for that time zone; hence, AST is related to the
    local standard time (LST)
    ASHRAE Fundamentals 2021 p14.9  Apparent Solar Time

    LST : local standard time, decimal hours
    date : current date at the location
    LON : longitude of site 100.57 for Bangkok, Thailand
    TZ : time zone, expressed in hours ahead or behind coordinated universal time (UTC) 
        UTC:+7 for THAILAND
        UTC:-5 for  Atlanta, GA
    """
    LSM = 15*TZ
    AST = LST + equation_of_time(n)/60 + (LON.m - LSM)/15
    return AST
