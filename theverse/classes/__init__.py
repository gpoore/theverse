# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from .base import Universe


# All `Primordial` subclasses must be imported here, so that they are
# instantiated and thus will appear in the class registry used by `Universe`.
from . import astronomy
