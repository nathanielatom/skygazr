# Skygazr

Locate celestial objects in the sky by name. 

# Installation

Built on the excellent skyfield library. Wikipedia is used for name lookup.

Install the following dependencies:

```
pip install skyfield pandas beautifulsoup4 wikipedia
```

# Usage

Example:

```
./skygazr.py --time "2020-10-03T00:35:20.381" --body "Betelgeuse"

To see Betelgeuse, look up 07deg 03' 38.5", and use a real compass to point to 86deg 28' 34.3" clockwise of North.
Relative to you, Betelgeuse is traveling 30.23 km/s ([11.24 27.63  4.92] velocity) and is 4.044e+15 km away from you.
```

If it's a planet or star in the Hipparcos Catalogue, will also show relative 
speed and distance. Constellations are unsupported.

Fun targets: 

```
"Betelgeuse"
"61 Cygni"
"Sagittarius A"
"Messier 87"
"Andromeda"
"Mars"
"Jupiter Barycenter"
```

