# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from ...classes import Universe

universe = Universe(
    name='Universe',
)

def load():
    from . import planetary_systems
    from . import stars
    from . import planets
load()
del load