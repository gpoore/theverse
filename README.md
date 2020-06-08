# The Verse – Properties of our universe (and others) for generating problems with realistic parameters

The Verse is a library of physical and other properties of our universe.  It
is intended for use in creating physics problems with realistic parameters.

The Verse is currently at an early stage of development.  At present, it only
contains part of the solar system—the Sun and a few planets, with only a few
properties each.  Eventually, it will contain a broader range of things from
our universe, such as more planetary data, stars, exoplanets, spacecraft and
other vehicles, animals, elements, and particles.  It will also eventually
contain things from various fictional verses.

Objects in the universe are represented as class instances.  For example, the
Sun is an instance of the class `Star`.  Physical properties are represented
via a subclass of
[`astropy.units.Quantity`](https://docs.astropy.org/en/stable/api/astropy.units.Quantity.html#astropy.units.Quantity).
This ensures that all properties have associated units.

