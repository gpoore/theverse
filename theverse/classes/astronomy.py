# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from .base import Primordial
from . import dimensions as dim




class PlanetarySystem(Primordial):
    _attr_linkdicts = [
        'stars',
        'planets',
    ]




class Star(Primordial):
    _attr_links = {
        'planetary_system': PlanetarySystem
    }
    _attr_linkdicts = [
        'planets',
    ]
    _attr_units = {
        'mass': dim.mass,
    }
    _attr_strings = [
        'spectral_type',
    ]




class Planet(Primordial):
    _attr_links = {
        'planetary_system': PlanetarySystem,
        'primary': Star,
    }
    _attr_units = {
        'mass': dim.mass,
        'radius': dim.length,
        'volumetric_mean_radius': dim.length,
        'equatorial_radius': dim.length,
        'polar_radius': dim.length,
    }
    _attr_fallbacks = {
        'radius': ('equatorial_radius', 'volumetric_mean_radius'),
        'star': 'primary',
    }
