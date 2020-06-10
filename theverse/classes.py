# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


import re
from typing import Dict, List, Optional, Tuple, Union
import astropy.units
import astropy.units.si as si
from .err import TheVerseError




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
    reference URL for its value.  A quantity will typically be used as an
    attribute of a Python object that represents a material object.  In this
    case, `.link_object()` is used to set the quantity's `.object` to the
    object, set its name to the standard value used by the object, and check
    that the quantity's units are as expected.

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

    def link_object(self, obj, attr_name, expected_unit):
        if self._object is not None:
            raise TheVerseError(f'"{self.name}" ({self.__class__.__name___}) is already linked to '
                                f'"{self._object.name}" ({self._object.__class__.__name__})')
        self._object = obj
        self._name = attr_name
        if self.unit != expected_unit:
            raise TypeError(f'Invalid unit for "{obj.name}" attribute "{attr_name}"; expected "{expected_unit}", not "{self.unit}"')

    def unlink_object(self, object):
        if self._object is object:
            if not object.unlinking:
                raise TheVerseError('Can only unlink an object by calling its ".unlink()" method')
            self._object = None




class LinkDict(dict):
    '''
    A dict subclass for mapping the names of material objects to Python
    objects that represent represent them.

    Does not implement `__setitem__` and `__delitem__`; `.link_object()` and
    `.unlink_object()` are provided instead.  This provides a uniform
    interface for all linking/unlinking and also makes `LinkDict` behave more
    like a frozen dict.

    Values can be accessed as attributes.
    '''
    def __init__(self):
        super().__init__()
        self._attr_names = {}

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def setdefault(self, key, value=None):
        raise NotImplementedError

    def link_object(self, object: 'Everything'):
        name = object.name
        super().__setitem__(name, object)
        self._attr_names[object.name.lower().replace(' ', '_')] = object.name

    def unlink_object(self, object: 'Everything'):
        if not object.unlinking:
            raise TheVerseError('Can only unlink an object by calling its ".unlink()" method')
        super().__delitem__(object.name)

    def __getattr__(self, attr):
        try:
            key = self._attr_names[attr.lower()]
        except KeyError:
            raise KeyError(attr)
        return self[key]




class Everything(object):
    '''
    Base class for representing material objects.  Attributes are typically
    `Quantity` instances or dicts mapping names to instances.
    '''
    # Map attributes to expected units
    _attr_units: Dict[str, Optional[astropy.units.Unit]] = {}
    # Map attributes to fallback attributes when they do not exist
    _attr_fallbacks: Dict[str, Union[str, List[str], Tuple[str]]] = {}
    # Map attributes to names, which are used by quantities
    _attr_names: Dict[str, str] = {}

    def __init__(self, name: str, **kwargs):
        if type(self) is Everything:
            raise TheVerseError(f'{self.__class__} cannot be instantiated; only subclasses can be used')

        if not isinstance(name, str):
            raise TypeError
        self._name = name

        reference = kwargs.pop('reference', None)
        reference_url = kwargs.pop('reference_url', None)
        if kwargs and reference is None and reference_url is None:
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
        # Whether unlinking is currently in progress
        self._unlinking = False

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
                    if k in self._attr_names:
                        quant.link_object(self, self._attr_names[k], expected_unit)
                    else:
                        quant.link_object(self, k.replace('_', ' '), expected_unit)
                    getattr(self, f'_set_{k}')(quant)
            elif expected_unit is None:
                setattr(self, k, v)
            else:
                if isinstance(v, Quantity):
                    quant = v
                else:
                    quant = Quantity(v, reference=self.reference, reference_url=self.reference_url)
                if k in self._attr_names:
                    quant.link_object(self, self._attr_names[k], expected_unit)
                else:
                    quant.link_object(self, k.replace('_', ' '), expected_unit)
                setattr(self, k, quant)

    def __getattr__(self, attr):
        try:
            alias_or_aliases = self._attr_fallbacks[attr]
        except KeyError:
            raise AttributeError(f"{self.__class__}' object has no attribute {attr}")
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
    def unlinking(self):
        return self._unlinking

    def unlink(self):
        '''
        Remove all references to this instance from other instances, so that
        this instance does not exist as far as they are concerned.  Also
        remove all references from Quantity attributes.
        '''
        self._unlinking = True
        for d in self._links:
            d.unlink_object(self)
        for v in self.__dict__.values():
            try:
                v.unlink_object(self)
            except AttributeError:
                pass
        self._unlinking = False
        self._links = []



class Universe(Everything):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        if name in self.universes:
            raise TheVerseError(f'Universe "{name}" already exists')
        self.universes.link_object(self)

        for name in Primordial.registry:
            setattr(self, f'{name.lower()}s', LinkDict())

    universes: Dict[str, 'Universe'] = LinkDict()




class MetaPrimordial(type):
    def __new__(cls, name, parents, attr_dict):
        if not hasattr(cls, 'registry'):
            cls.registry: Dict[str, Primordial] = {}
        else:
            cls.registry[name] = cls
        return super().__new__(cls, name, parents, attr_dict)


class Primordial(Everything, metaclass=MetaPrimordial):
    def __init__(self, name, **kwargs):
        if type(self) is Primordial:
            raise TheVerseError(f'{self.__class__} cannot be instantiated; only subclasses can be used')

        universe = kwargs.pop('universe', 'Universe')
        if isinstance(universe, str):
            try:
                universe = Universe.universes[universe]
            except KeyError:
                raise TheVerseError(f'Universe "{universe}" does not exist')
        elif not isinstance(universe, Universe):
            raise TypeError
        self.universe = universe
        super().__init__(name, **kwargs)
        registry = getattr(universe, f'{self.__class__.__name__.lower()}s')
        if name in registry:
            raise TheVerseError(f'{self.__class__.__name__} "{name}" already exists in universe "{universe.name}"')
        registry.link_object(self)
        self._links.append(registry)




class Star(Primordial):
    _attr_units = {
        'universe': None,
        'mass': mass,
        'spectral_type': None,
    }

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.planets: Dict[str, Planet] = LinkDict()

    def unlink(self):
        for planet in self.planets:
            delattr(planet, 'primary')
        super().unlink()




class Planet(Primordial):
    _attr_units = {
        'universe': None,
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

    def _set_primary(self, primary):
        if isinstance(primary, Star):
            pass
        elif isinstance(primary, str):
            try:
                primary = self.universe.stars[primary]
            except KeyError:
                raise TheVerseError(f'Star "{primary}" does not exist in universe "{self.universe.name}"')
        else:
            raise TypeError('Expected Star object or star name string')
        primary.planets.link_object(self)
        self._links.append(primary.planets)
        self.primary = primary



Universe(
    name='Universe',
)

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
