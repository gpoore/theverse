# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


import collections
import importlib
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




class RefStr(str):
    '''
    String that also provides reference information.
    '''
    def __new__(cls,
                string: str,
                *,
                name=None,
                reference: Optional[str]=None,
                reference_url: Optional[str]=None):
        inst = super().__new__(cls, string)
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

    @property
    def name(self):
        return self._name

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




class LinkDict(Dict[str, 'Everything']):
    '''
    A dict subclass for mapping the names of material objects to Python
    objects that represent them.

    Does not implement `__setitem__` and `__delitem__`; `.link_object()` and
    `.unlink_object()` are provided instead.  This provides a uniform
    interface for all linking/unlinking and also makes `LinkDict` behave more
    like a frozen dict.

    Values can be accessed as attributes.
    '''
    def __init__(self, *, registry=False):
        super().__init__()
        self._attr_names = {}
        self.registry = registry

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
        name_normalized = object.name.lower().replace(' ', '_')
        if name_normalized in self._attr_names:
            if self.registry:
                if self._attr_names[name_normalized] == name:
                    raise TheVerseError(f'"{object.name}" ({object.__class__.__name__}) already exists')
                raise TheVerseError(f'"{object.name}" ({object.__class__.__name__}) conflicts with existing object '
                                    f'named "{self._attr_names[name_normalized]}"; names must be unique when lowercased')
            if self._attr_names[name_normalized] != name:
                raise TheVerseError(f'"{object.name}" ({object.__class__.__name__}) conflicts with existing object '
                                    f'named "{self._attr_names[name_normalized]}"; names must be unique when lowercased')
        super().__setitem__(name, object)
        self._attr_names[name_normalized] = object.name

    def unlink_object(self, object: 'Everything'):
        if not object.unlinking:
            raise TheVerseError('Can only unlink an object by calling its ".unlink()" method')
        try:
            super().__delitem__(object.name)
        except KeyError:
            pass

    def __getattr__(self, attr):
        try:
            key = self._attr_names[attr.lower()]
        except KeyError:
            raise KeyError(attr)
        return self[key]




def _class_name_to_name_and_collection_name(class_name):
    name = re.sub('^[A-Z]', lambda m: m.group().lower(), class_name)
    name = re.sub('[A-Z]', lambda m: '_' + m.group().lower(), name)
    if not name.endswith('s'):
        collection_name = name + 's'
    else:
        collection_name = name + 'es'
    return (name, collection_name)

_attr_re = re.compile(r'^[a-z]+(?:_[a-z]+)*$')


class MetaEverything(type):
    '''
    Metaclass for base class.  Performs extensive attribute checking so that
    base class subclasses remain reliable as they increase in number and so
    that less checking is needed for instances.
    '''
    def __new__(cls, name, parents, attr_dict):
        name, collection_name = _class_name_to_name_and_collection_name(name)
        if '_link_name' not in attr_dict:
            attr_dict['_link_name'] = name
        if '_link_collection_name' not in attr_dict:
            attr_dict['_link_collection_name'] = collection_name

        try:
            _attr_links = attr_dict['_attr_links']
        except KeyError:
            pass
        else:
            if not isinstance(_attr_links, dict):
                raise TypeError
            if not all(isinstance(k, str) and _attr_re.match(k) and issubclass(v, Everything)
                       for k, v in _attr_links.items()):
                raise TypeError

        try:
            _attr_linkdicts = attr_dict['_attr_linkdicts']
        except KeyError:
            pass
        else:
            if not any(isinstance(_attr_linkdicts, t) for t in (list, tuple)):
                raise TypeError
            if not all(isinstance(x, str) and _attr_re.match(x)
                       for x in _attr_linkdicts):
                raise TypeError

        try:
            _attr_units = attr_dict['_attr_units']
        except KeyError:
            pass
        else:
            if not isinstance(_attr_units, dict):
                raise TypeError
            if not all(isinstance(k, str) and _attr_re.match(k) and isinstance(v, astropy.units.UnitBase)
                       for k, v in _attr_units.items()):
                raise TypeError

        try:
            _attr_strings = attr_dict['_attr_strings']
        except KeyError:
            pass
        else:
            if not any(isinstance(_attr_strings, t) for t in (list, tuple)):
                raise TypeError
            if not all(isinstance(x, str) and _attr_re.match(x)
                       for x in _attr_strings):
                raise TypeError

        try:
            _attr_fallbacks = attr_dict['_attr_fallbacks']
        except KeyError:
            pass
        else:
            if not isinstance(_attr_fallbacks, dict):
                raise TypeError
            if not all(isinstance(k, str) and _attr_re.match(k)
                       for k in _attr_fallbacks):
                raise TypeError
            if not all((isinstance(v, str) and not v.startswith('_')) or
                       (any(isinstance(v, t) for t in (list, tuple)) and
                        all(isinstance(x, str) and _attr_re.match(x) for x in v))
                       for v in _attr_fallbacks.values()):
                raise TypeError

        try:
            _attr_quant_names = attr_dict['_attr_quant_names']
        except KeyError:
            pass
        else:
            if not isinstance(_attr_quant_names, dict):
                raise TypeError
            if not all(isinstance(k, str) and _attr_re.match(k) and isinstance(v, str)
                       for k, v in _attr_quant_names.items()):
                raise TypeError

        return super().__new__(cls, name, parents, attr_dict)




class Everything(object, metaclass=MetaEverything):
    '''
    Base class for representing material objects.  Attributes are typically
    `Quantity` instances or dicts mapping names to instances (`LinkDict`).
    '''
    # Map attribute names to expected `Everything` subclasses
    _attr_links: Dict[str, 'Everything'] = {}
    # List attribute names that are LinkDicts
    _attr_linkdicts: List[str] = []
    # Map attribute names to expected units
    _attr_units: Dict[str, astropy.units.Unit] = {}
    # List attribute names that are strings
    _attr_strings: List[str] = []
    # Map attribute names to fallback attribute names when they do not exist
    _attr_fallbacks: Dict[str, Union[str, List[str], Tuple[str]]] = {}
    # Map attribute names to optional alternate names used by quantities
    _attr_quant_names: Dict[str, str] = {}

    # Subclasses that are actually instantiated must also implement these:
    #
    #   _link_name: str             Default attribute name for when an
    #                               instance is used as an attribute.
    #
    #   _link_collection_name: str  Default attribute name for when a
    #                               collection of instances is used as an
    #                               attribute.

    def __init__(self, name: str, **kwargs):
        if type(self) is Everything:
            raise TheVerseError(f'{self.__class__} cannot be instantiated; only subclasses can be used')

        if not isinstance(name, str):
            raise TypeError
        self._name = name

        reference = kwargs.pop('reference', None)
        reference_url = kwargs.pop('reference_url', None)
        if kwargs and reference is None and reference_url is None:
            raise TypeError('At least one of "reference" and "reference_url" must be given')
        if any(x is not None and not isinstance(x, str) for x in (reference, reference_url)):
            raise TypeError
        self._reference: Optional[str] = reference
        self._reference_url: Optional[str] = reference_url

        # List of all objects that link to this instance.  This allows
        # unlinking, which removes all references from other objects to this
        # instance (so that this instance does not exist as far as they are
        # concerned), but does not actually delete this instance.
        self._links = []
        # Whether unlinking is currently in progress.  An instance can only
        # call `.unlink_object()` on other instances that reference it when
        # `._unlinking == True`.
        self._unlinking = False

        for k, v in kwargs.items():
            try:
                expected_type = self._attr_links[k]
            except KeyError:
                pass
            else:
                if not isinstance(v, expected_type):
                    raise TypeError
                getattr(self, f'_proc_{k}', self._linkdictproc)(v)
                setattr(self, k, v)
                v.link_object(self)
                continue
            if k in self._attr_strings:
                if isinstance(v, RefStr):
                    pass
                elif isinstance(v, str):
                    v = RefStr(v, reference=self.reference, reference_url=self.reference_url)
                else:
                    raise TypeError
                try:
                    v._name = self._attr_quant_names[k]
                except KeyError:
                    v._name = k.replace('_', ' ')
                v.link_object(self)
                setattr(self, k, v)
                continue
            try:
                expected_unit = self._attr_units[k]
            except KeyError:
                raise TypeError(f'Unknown keyword argument "{k}"')
            if isinstance(v, Quantity):
                quant = v
            else:
                quant = Quantity(v, reference=self.reference, reference_url=self.reference_url)
            if quant.unit != expected_unit:
                raise TypeError(f'Invalid unit for "{self.name}" attribute "{k}"; '
                                f'expected "{expected_unit}", not "{quat.unit}"')
            try:
                quant._name = self._attr_quant_names[k]
            except KeyError:
                quant._name = k.replace('_', ' ')
            quant.link_object(self)
            setattr(self, k, quant)

        for k in self._attr_linkdicts:
            setattr(self, k, LinkDict())

    def __getattr__(self, attr):
        # No need to check for invalid alias keys; that is done in
        # MetaEverything
        try:
            alias_or_aliases = self._attr_fallbacks[attr]
        except KeyError:
            raise AttributeError(f'{self.__class__} has no attribute {repr(attr)}')
        if isinstance(alias_or_aliases, str):
            alias = alias_or_aliases
            try:
                val = self.__dict__[alias]
            except KeyError:
                raise AttributeError(f'{self.__class__} has no attribute {repr(attr)}')
            return val
        aliases = alias_or_aliases
        for alias in aliases:
            try:
                val = self.__dict__[alias]
            except KeyError:
                pass
            else:
                return val
        raise AttributeError(f'{self.__class__} has no attribute {repr(attr)}')

    def _linkdictproc(self, object: 'Everything'):
        linkdict = getattr(object, self._link_collection_name)
        linkdict.link_object(self)
        self._links.append(linkdict)

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

    def link_object(self, object: Union[LinkDict, 'Everything']):
        self._links.append(object)

    def unlink_object(self, object: 'Everything'):
        if not object.unlinking:
            raise TheVerseError('Can only unlink an object by calling its ".unlink()" method')
        for k in self._attr_links:
            try:
                attr = getattr(self, k)
            except AttributeError:
                pass
            else:
                if attr is object:
                    delattr(self, k)

    def unlink(self):
        '''
        Remove all references to this instance from other instances, so that
        this instance does not exist as far as they are concerned.  Also
        remove all references from Quantity attributes.
        '''
        self._unlinking = True
        for x in self._links:
            x.unlink_object(self)
        self._unlinking = False
        self._links = []




class Universe(Everything):
    universes: LinkDict = LinkDict(registry=True)
    default_name = 'Universe'

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

        self.universes.link_object(self)
        self._links.append(self.universes)

        for cls in Primordial.registry.values():
            setattr(self, cls._link_collection_name, LinkDict(registry=True))
            try:
                importlib.import_module(f'.data.{self._link_name}.{cls._link_collection_name}', 'theverse')
            except ImportError:
                pass




class MetaPrimordial(MetaEverything):
    def __new__(cls, name, parents, attr_dict):
        if not hasattr(cls, 'registry'):
            # The order of types in the registry is significant because this
            # sets import order and thus object creation order in each
            # universe.  For example, planetary systems are created before
            # stars, so that stars can reference them, and stars are created
            # before planets, so planets can reference them.  To ensure order
            # under Python <3.7, need OrderedDict.
            cls.registry: Dict[str, Primordial] = collections.OrderedDict()
            return super().__new__(cls, name, parents, attr_dict)
        new_class = super().__new__(cls, name, parents, attr_dict)
        cls.registry[attr_dict['_link_name']] = new_class
        return new_class


class Primordial(Everything, metaclass=MetaPrimordial):
    '''
    Base class for everything within a universe.
    '''
    def __init__(self, name, **kwargs):
        if type(self) is Primordial:
            raise TheVerseError(f'{self.__class__} cannot be instantiated; only subclasses can be used')

        universe = kwargs.pop('universe', Universe.default_name)
        if isinstance(universe, str):
            try:
                universe = Universe.universes[universe]
            except KeyError:
                raise TheVerseError(f'Universe "{universe}" does not exist')
        elif not isinstance(universe, Universe):
            raise TypeError
        self.universe = universe
        registry = getattr(universe, self._link_collection_name)
        for k, v in kwargs.items():
            if k in self._attr_links and isinstance(v, str):
                try:
                    obj_cls = self._attr_links[k]
                    obj_registry = getattr(universe, obj_cls._link_collection_name)
                    obj = obj_registry[v]
                except KeyError:
                    raise TheVerseError(f'"{v}" ({v.__class__.__name__}) does not exist in universe "{universe.name}"')
                kwargs[k] = obj
        super().__init__(name, **kwargs)
        registry.link_object(self)
        self._links.append(registry)




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
        'mass': mass,
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
        'mass': mass,
        'radius': length,
        'volumetric_mean_radius': length,
        'equatorial_radius': length,
        'polar_radius': length,
    }
    _attr_fallbacks = {
        'radius': ('equatorial_radius', 'volumetric_mean_radius'),
        'star': 'primary',
    }
