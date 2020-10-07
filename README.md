# Skygazr

Locate celestial objects in the sky by name. 

# Installation

Built on the excellent skyfield library. Wikipedia is used for name lookup.

Install the following dependencies:

```
pip install skyfield pandas beautifulsoup4 wikipedia
```

# Usage

Example: ./skygazr.py --time "2020-10-03T00:35:20.381" --body "Betelgeuse"

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

