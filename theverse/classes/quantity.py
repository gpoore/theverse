# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


import re
from typing import Optional, Union
import astropy.units
from ..err import TheVerseError




class Quantity(astropy.units.Quantity):
    '''
    Version of Astropy's `Quantity` for describing the physical and other
    properties of a material object while providing references for those
    values.  Inspired by Astropy's `Constant`.  A material object is
    represented as a Python object whose attributes are `Quantity` instances.

    A quantity may optionally have a name.  It must have a reference or a
    reference URL for its value.  A quantity will typically be used as an
    attribute of a Python object that represents a material object.  In this
    case, `.link_object()` is used to set the quantity's `.object` to the
    object.

    `Quantity()` can take a string `value` in which underscores are used as a
    digit separator (for example, `1_234.567_890 kg`).

    `Quantity` units are always SI units.

    Astropy references:
      * https://docs.astropy.org/en/stable/api/astropy.units.Quantity.html
      * https://docs.astropy.org/en/stable/api/astropy.constants.Constant.html
    '''
    def __new__(cls,
                value: Union[str, astropy.units.Quantity],
                unit: Optional[Union[str, astropy.units.Unit]]=None,
                *,
                name=None,
                reference: Optional[str]=None,
                reference_url: Optional[str]=None,
                **kwargs):
        if isinstance(value, str):
            value = cls._num_underscore_sep_strip(value)
        inst = super().__new__(cls, value, unit, **kwargs)
        inst = inst.si
        if name is not None and not isinstance(name, str):
            raise TypeError
        inst._name = name
        inst._object = None
        if reference is None and reference_url is None:
            raise TypeError('At least one of "reference" and "reference_url" must be given')
        if any(x is not None and not isinstance(x, str) for x in (reference, reference_url)):
            raise TypeError
        inst._reference = reference
        inst._reference_url = reference_url
        return inst

    @staticmethod
    def _num_underscore_sep_strip(num_str, _regex=re.compile(r'(?<=[0-9])_(?=[0-9])')):
        return _regex.sub(r'', num_str)

    def __repr__(self):
        return (f'<{self.__class__} '
                f'name={repr(self.name)} '
                f'value={self.value} unit={repr(self.unit)} '
                f'reference={repr(self.reference)} '
                f'reference_url={repr(self.reference_url)} '
                f'object={repr(self.object)}>')

    @property
    def name(self):
        return self._name

    @property
    def object(self):
        return self._object

    @property
    def reference(self):
        return self._reference

    @property
    def reference_url(self):
        return self._reference_url

    def link_object(self, object):
        if self._object is not None:
            raise TheVerseError(f'"{self.name}" ({self.__class__.__name__}) is already linked to '
                                f'"{self._object.name}" ({self._object.__class__.__name__})')
        self._object = object

    def unlink_object(self, object):
        if self._object is object:
            if not object.unlinking:
                raise TheVerseError('Can only unlink an object by calling its ".unlink()" method')
            self._object = None
