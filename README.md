# The Verse – Find properties of objects in our universe (and others) without leaving Python



The Verse is a Python library of properties of objects in our universe, such
as the mass and radius of the Earth and other planets.

Though The Verse can be useful for reference purposes, it is primarily being
developed for use in generating physics, astronomy, and chemistry problems
with realistic parameters.  For example, a random planet can be chosen from
the Solar System, and then its mass and radius can be used to generate a
problem that involves calculating gravitational acceleration based on those
properties.

The Verse is currently at an early stage of development.  At present, it only
contains part of the Solar System—the Sun and a few planets, with only a few
properties each.  Eventually, it will contain a broader range of things from
our universe, such as more planetary data, stars, exoplanets, spacecraft and
other vehicles, animals, elements, and particles.  It will also eventually
contain things from various fictional verses.



## Example

```pycon
>>> import theverse
>>> print(theverse.earth.equatorial_radius)
6378137.0 m
>>> for planet_name, planet_obj in theverse.solar_system.planets.items():
...     print(f'{planet_name: <10}  {planet_obj.mass}')
...
Mercury     3.3011e+23 kg
Venus       4.8675e+24 kg
Earth       5.9724e+24 kg
>>> print(theverse.earth.primary.name)
Sun
>>> print(theverse.earth.primary.mass)
1.9885e+30 kg
>>> print(theverse.sun.reference_url)
https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html
>>> for star_name in theverse.universe.stars:
...     print(star_name)
...
Sun
```


## Installation

Install **Python 3.6+** if it is not already available on your machine.  See
https://www.python.org/, or use the package manager or app store for your
operating system.  Because The Verse requires
[Astropy](https://www.astropy.org/) and its dependencies (which include
[NumPy](https://numpy.org/)), you may want to consider a Python distribution
like [Anaconda](https://www.anaconda.com/distribution/) instead.

Install
[setuptools](https://packaging.python.org/tutorials/installing-packages/)
for Python if it is not already installed.  This can be accomplished by
running
```
python -m pip install setuptools
```
on the command line.  Depending on your system, you may need to use `python3`
instead of `python`.  This will often be the case for Linux and OS X.

Install [Astropy](https://www.astropy.org/) if it is not already installed.

Install `theverse` by running this on the command line:
```
python -m pip install theverse
```
Depending on your system, you may need to use `python3` instead of `python`.
This will often be the case for Linux and OS X.


### Upgrading

```
python -m pip install theverse --upgrade
```
Depending on your system, you may need to use `python3` instead of `python`.
This will often be the case for Linux and OS X.


### Installing the development version

If you want to install the development version to use the latest features,
download `theverse` from [GitHub](https://github.com/gpoore/theverse), extract
the files, and then run
```
python setup.py install
```
Depending on your system, you may need to use `python3` instead of `python`.
This will often be the case for Linux and OS X.



## Technical details

Objects in the universe are represented as class instances.  For example, the
Sun is an instance of the class `Star`.

Physical properties are represented via a subclass of
[`astropy.units.Quantity`](https://docs.astropy.org/en/stable/api/astropy.units.Quantity.html#astropy.units.Quantity).
This ensures that all quantities have associated units.  Quantities also have
`reference` and `reference_url` attributes that provide information about the
source of values.

Collections of objects, like `theverse.universe.stars`, are instances of a
dict subclass.  For example, `theverse.universe.stars` maps star names
(strings) to instances of the class `Star`.  The dict subclass used in these
cases allows values to be accessed normally (`theverse.universe.stars['Sun']`)
and also as lowercased attributes (`theverse.universe.stars.sun`).  The dict
subclass does not support standard dict methods for adding or deleting keys;
data should typically be treated as immutable once it is loaded.


