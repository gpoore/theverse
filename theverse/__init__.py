# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from .version import __version__, __version_info__


from .data.universe import universe
solar_system = universe.planetary_systems.solar_system
sun = universe.stars.sun
earth = universe.planets.earth
