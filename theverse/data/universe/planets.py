# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from ...classes.astronomy import Planet


Planet(
    name='Mercury',
    reference='Williams, D.R. (27 September 2018). "Mercury Fact Sheet". NASA Goddard Space Flight Center.',
    reference_url='https://nssdc.gsfc.nasa.gov/planetary/factsheet/mercuryfact.html',
    planetary_system='Solar System',
    primary='Sun',
    mass='0.33011e24 kg',
    equatorial_radius='2439.7 km',
    polar_radius='2439.7 km',
    volumetric_mean_radius='2439.7 km',
)


Planet(
    name='Venus',
    reference='Williams, D.R. (27 September 2018). "Venus Fact Sheet". NASA Goddard Space Flight Center.',
    reference_url='https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html',
    planetary_system='Solar System',
    primary='Sun',
    mass='4.8675e24 kg',
    equatorial_radius='6051.8 km',
    polar_radius='6051.8 km',
    volumetric_mean_radius='6051.8 km',
)


Planet(
    name='Earth',
    reference='Williams, D.R. (02 April 2020). "Earth Fact Sheet". NASA Goddard Space Flight Center.',
    reference_url='https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html',
    planetary_system='Solar System',
    primary='Sun',
    mass='5.9724e24 kg',
    equatorial_radius='6378.137 km',
    polar_radius='6356.752 km',
    volumetric_mean_radius='6371.000 km',
)
