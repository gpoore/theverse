# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


import re
from typing import Dict, List, Optional, Union
import astropy.units
import astropy.units.si as si
from .err import TheVerseError
from .util import KeyDefaultDict




# Units for dimensional analysis checks
mass = si.kg
length = si.m
time = si.s
speed = length/time




class Quantity(astropy.units.Quantity):
    '''
    Version of Astropy's `Quantity` for describing the physical and other
    properties of a material object while providing references for those
    values.  Inspired by Astropy's `Constant`.  A material object is
    represented as a Python object whose attributes are `Quantity` instances.

    A quantity may optionally have a name.  It must have a reference or a
    reference URL.  A quantity will typically be used as an attribute of a
    Python object that represents a material object.  In this case,
    `.link_to_object()` is used to set the quantity's `.object` to the object,
    set its name to the standard value used by the object, and ensure that the
    quantity's units are as expected.

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
            raise TheVerseError('At least one of "reference" and "reference_url" must be given')
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
                f'value={self.value} unit={repr(self.unit)} '
                f'name={repr(self.name)} '
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

    def link_to_object(self, obj, attr_name, expected_unit):
        if self._object is not None:
            raise TheVerseError(f'{self.__class__.__name___} is already linked to "{self._object.name}" ({self._object.__class__.__name__})')
        self._object = obj
        self._name = attr_name
        if self.unit != expected_unit:
            raise TypeError(f'Invalid unit for "{obj.name}" attribute "{attr_name}"; expected "{expected_unit}", not "{self.unit}"')




class MetaPrimordial(type):
    '''
    Metaclass for the class that is used to represent material objects.
    '''
    @property
    def registry(cls):
        return cls._registry


class Primordial(object, metaclass=MetaPrimordial):
    '''
    Base class for representing material objects.  Attributes are typically
    `Quantity` instances or dicts mapping names to Primordial instances.
    '''
    _registry: Dict[str, 'Primordial'] = {}

    _attr_units: Dict[str, Optional[astropy.units.Unit]] = {}

    _attr_fallbacks: Dict[str, Union[str, list, tuple]] = {}

    _attr_alt_names: 'KeyDefaultDict[str, str]' = KeyDefaultDict(lambda s: s.replace('_', ''))

    def __init__(self, name: str, **kwargs):
        if type(self) is Primordial:
            raise TheVerseError('The base class cannot be instantiated; only subclasses can be used')
        if not isinstance(name, str):
            raise TypeError
        self._name = name
        if name in self._registry:
            raise TheVerseError(f'Object "{name}" already exists')
        self._registry[name] = self

        reference = kwargs.pop('reference', None)
        reference_url = kwargs.pop('reference_url', None)
        if reference is None and reference_url is None:
            raise TheVerseError('At least one of "reference" and "reference_url" must be given')
        if any(x is not None and not isinstance(x, str) for x in (reference, reference_url)):
            raise TypeError
        self._reference: Optional[str] = reference
        self._reference_url: Optional[str] = reference_url

        # List of all dicts that link other Primordial instances to this
        # instance.  This allows unlinking, which removes all references from
        # other instances to this instance (so that this instance does not
        # exist as far as they are concerned), but does not actually delete
        # this instance.
        self._links = []

        for k, v in kwargs.items():
            try:
                expected_unit = self._attr_units[k]
            except KeyError:
                raise TypeError(f'Unknown keyword argument "{k}"')
            if hasattr(self, f'_set_{k}'):
                if expected_unit is None:
                    getattr(self, f'_set_{k}')(v)
                else:
                    if isinstance(v, Quantity):
                        quant = v
                    else:
                        quant = Quantity(v, reference=self.reference, reference_url=self.reference_url)
                    quant.link_to_object(self, self._attr_alt_names[k], expected_unit)
                    getattr(self, f'_set_{k}')(quant)
            elif expected_unit is None:
                setattr(self, k, v)
            else:
                if isinstance(v, Quantity):
                    quant = v
                else:
                    quant = Quantity(v, reference=self.reference, reference_url=self.reference_url)
                quant.link_to_object(self, self._attr_alt_names[k], expected_unit)
                setattr(self, k, quant)

    def __getattr__(self, attr):
        try:
            alias_or_aliases = self._attr_fallbacks[attr]
        except KeyError:
            raise AttributeError(f"{repr(self.__class__)}' object has no attribute {repr(attr)}")
        if isinstance(alias_or_aliases, str):
            alias = alias_or_aliases
            try:
                val = self.__dict__[alias]
            except KeyError:
                raise AttributeError(f"'{self.__class__}' object has no attribute '{attr}'")
            return val
        aliases = alias_or_aliases
        for alias in aliases:
            try:
                val = self.__dict__[alias]
            except KeyError:
                pass
            else:
                return val
        raise AttributeError(f"'{self.__class__}' object has no attribute '{attr}'")

    @property
    def name(self):
        return self._name

    @property
    def reference(self):
        return self._reference

    @property
    def reference_url(self):
        return self._reference_url

    @property
    def registry(self):
        return self._registry

    def unlink(self):
        '''
        Remove all references to this Primordial instance from other
        Primordial instances, so that this instance does not exist as far as
        they are concerned.  Also remove all references from Quantity
        attributes.
        '''
        for d in self._links:
            del d[self.name]
        del self._registry[self.name]
        for v in self.__dict__.values():
            if isinstance(v, Quantity):
                v._object = None




class Star(Primordial):
    _registry = {}

    _attr_units = {
        'mass': mass,
        'spectral_type': None,
    }

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.planets: Dict[str, Planet] = {}

    def unlink(self):
        for planet in self.planets:
            delattr(planet, 'primary')
        super().unlink()




class Planet(Primordial):
    _registry = {}

    _attr_units = {
        'mass': mass,
        'primary': None,
        'radius': length,
        'volumetric_mean_radius': length,
        'equatorial_radius': length,
        'polar_radius': length,
    }

    _attr_fallbacks = {
        'radius': ('equatorial_radius', 'volumetric_mean_radius'),
        'star': 'primary',
    }

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

    def _set_primary(self, primary):
        if isinstance(primary, Star):
            pass
        elif isinstance(primary, str):
            try:
                primary = Star._registry[primary]
            except KeyError:
                raise TheVerseError(f'Star "{primary}" does not exist')
        else:
            raise TypeError('Expected Star object or star name string')
        primary.planets[self.name] = self
        self._links.append(primary.planets)
        self.primary = primary



Star(
    name='Sun',
    reference='Williams, D.R. (23 February 2018). "Sun Fact Sheet". NASA Goddard Space Flight Center.',
    reference_url='https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html',
    mass='1_988_500e24 kg',
    spectral_type='G2 V',
)

Planet(
    name='Earth',
    reference='Williams, D.R. (02 April 2020). "Earth Fact Sheet". NASA Goddard Space Flight Center.',
    reference_url='https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html',
    primary='Sun',
    mass='5.9724e24 kg',
    equatorial_radius='6378.137 km',
    polar_radius='6356.752 km',
    volumetric_mean_radius='6371.000 km',
)
