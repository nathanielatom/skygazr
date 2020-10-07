#!/usr/bin/env python
"""
Find out where Mars is, in the sky at P'diddy Island, PEI, ON, Canada.

Stellar info from the 1993 Hipparcos Catalogue, planets from DE421, and satellites from

Searches names with wikipedia. Constellations are unsupported.

Fun targets: "Betelgeuse", "61 Cygni", "Sagittarius A", "Messier 87", "Andromeda", "Mars", "Jupiter Barycenter"


TODO:

"ISS (ZARYA)", "Europa", "Titan"

use termux elevation, coordinates and possibly orientation

moar moons:

In [12]: jupiter = load('jup310.bsp')
[#################################] 100% jup310.bsp

In [13]: planets = load('de430t.bsp')
[#################################] 100% de430t.bsp

Saturn and further moons? Europa? Titan? Triton? Pluto?

sats:

In [33]: stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'

In [34]: satellites = load.tle_file(stations_url)
[#################################] 100% stations.txt

In [35]: print('Loaded', len(satellites), 'satellites')
Loaded 67 satellites

In [36]: by_name = {sat.name: sat for sat in satellites}

In [37]: by_name['ISS (ZARYA)']
Out[37]: <EarthSatellite ISS (ZARYA) catalog #25544 epoch 2020-09-19 20:33:04 UTC>

"""

import argparse

parser = argparse.ArgumentParser(description='Locate celestial objects in the sky.\nExample: ./skygazr.py --time "2020-10-03T00:35:20.381" --body "Betelgeuse"')
parser.add_argument('-s', '--space', '--latlong', nargs=2, type=float, default=(43.660444, -79.398556), help='Spatial coordinates of observation, given as two floating point values in degrees for latitude and longitude on the surface of Earth. Default is the Burton Tower, University of Toronto Physics Library, Toronto, Ontario, Canada (since, naturally, Toronto is the center of the universe ;).')
parser.add_argument('-e', '--elevation', type=float, default=100, help='Elevation of the observation, in meters above the surface of Earth.')
parser.add_argument('-t', '--time', '--at', type=str, default='now', help='Observation timestamp, in ISO 8601 format. Default is not the past, which is history, nor the future, which is a mystery, but a gift, and thus, the present.')
parser.add_argument('-z', '--timezone', type=str, default='local', help='timezone; TODO: implement')
parser.add_argument('-b', '--target', '--body', type=str, default='mars', help='Target celestial body to locate in the sky!')
args = parser.parse_args()

# import after argparse for faster CLI
from datetime import datetime, timezone

# ! pip install skyfield pandas beautifulsoup4 wikipedia
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from bs4 import BeautifulSoup
import wikipedia

GIGAPARSEC = 2.0626e+14 # au

def parse(string):
    # strip citation, replace dumb unicode minus signs
    string = string.split('[')[0].replace('−', '-').replace('–', '-')
    if '°' in string or 'h' in string:
        coordinates = tuple(float(num) for num in ''.join(char if char in {'.', '-'} or char.isdecimal() else ',' for char in string).split(',') if num)
    else:
        return ()
    return coordinates

def info_from_name_using_wikipedia(name):
    """
    Returns a dictionary for binary and multi-star systems. Constellations are unsupported.
    """
    hips = {}
    ra_hours, ra_degs, decs = {}, {}, {}
    page = wikipedia.page(name)
    soup = BeautifulSoup(page.html(), 'html.parser')
    table = soup.find('table', class_='infobox')
    entries = table.find_all('a', text='HIP')
    for entry in entries:
        hip = int(entry.next_sibling.strip().split(',')[0])
        key = entry.find_previous('b').text if len(entries) > 1 else name
        hips[key] = hip
    entries = table.find_all('a', text='Declination')
    for entry in entries:
        dec = parse(entry.find_next('td').text)
        key = entry.find_all_previous('b')[2].text if len(entries) > 1 else name
        decs[key] = dec or None
    entries = table.find_all('a', text='Right ascension')
    for entry in entries:
        ra_string = entry.find_next('td').text
        ra_hour = parse(ra_string) if 'h' in ra_string else None
        ra_deg = None if 'h' in ra_string else parse(ra_string)
        key = entry.find_all_previous('b')[1].text if len(entries) > 1 else name
        ra_hours[key] = ra_hour or None
        ra_degs[key] = ra_deg or None
    return hips, ra_hours, ra_degs, decs

def single_body(name):
    # TODO: warn if binary or multi-star system, picking arbitrarily
    pick_body = lambda bodies: bodies.get(name, next(iter(bodies.values())) if bodies else None)
    hips, ra_hours, ra_degs, decs = info_from_name_using_wikipedia(name)
    return pick_body(hips), pick_body(ra_hours), pick_body(ra_degs), pick_body(decs)

if __name__ == '__main__':
    stringy_body = args.target
    planets = load('de421.bsp')
    earth = planets['earth']
    try:
        target = planets[stringy_body]
    except (KeyError, ValueError) as error:
        with load.open(hipparcos.URL) as fi:
            catalog = hipparcos.load_dataframe(fi)
        if 'HIP' in stringy_body:
            target = Star.from_dataframe(catalog.loc[int(stringy_body.replace('HIP', ''))])
        else:
            hip, ra_hour, ra_deg, dec = single_body(stringy_body)
            if hip:
                target = Star.from_dataframe(catalog.loc[hip])
            else:
                target = Star(ra_hours=ra_hour, ra=ra_deg, dec_degrees=dec)

    # define spacetime coordinates
    latitude, longitude = args.space # deg
    elevation = args.elevation # m
    ts = load.timescale()
    timestamp = ts.now() if args.time == 'now' else ts.from_datetime(datetime.fromisoformat(args.time).astimezone(timezone.utc))
    location = earth + Topos(latitude_degrees=latitude, longitude_degrees=longitude, elevation_m=elevation)

    right_ascension, declination, equatorial_distance = earth.at(timestamp).observe(target).radec()
    observation = location.at(timestamp).observe(target)
    altitude, azimuth, distance = observation.apparent().altaz()

    velocity = observation.velocity.km_per_s
    speed = observation.speed().km_per_s

    print(f'To see {stringy_body}, look up {altitude}, and use a real compass to point to {azimuth} clockwise of North.')
    if distance.au < GIGAPARSEC:
        print(f'Relative to you, {stringy_body} is traveling {speed:0.4g} km/s ({velocity.round(2)} velocity) and is {distance.km:0.4g} km away from you.')
