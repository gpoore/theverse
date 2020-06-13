# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


'''
Base classes for representing material objects.
'''


import collections
import importlib
import re
from typing import Dict, List, Optional, Set, Tuple, Union
import astropy.units
from .refstr import RefStr
from .quantity import Quantity
from ..err import TheVerseError




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
            if not any(isinstance(_attr_linkdicts, t) for t in (list, set, tuple)):
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
            if not any(isinstance(_attr_strings, t) for t in (list, set, tuple)):
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
                       (any(isinstance(v, t) for t in (list, set, tuple)) and
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
    _attr_linkdicts: Union[List[str], Set[str], Tuple[str]] = []
    # Map attribute names to expected units
    _attr_units: Dict[str, astropy.units.Unit] = {}
    # List attribute names that are strings
    _attr_strings: Union[List[str], Set[str], Tuple[str]] = []
    # Map attribute names to fallback attribute names when they do not exist
    _attr_fallbacks: Dict[str, Union[str, List[str], Set[str], Tuple[str]]] = {}
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
    _universes: LinkDict = LinkDict(registry=True)
    default_name = 'Universe'

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.universes.link_object(self)
        self._links.append(self.universes)

    def __getattr__(self, attr):
        if attr in Primordial.link_collection_name_to_module_names_registry:
            for link_collection_name in Primordial.link_collection_name_to_module_names_registry[attr]:
                linkdict = LinkDict(registry=True)
                setattr(self, f'_{link_collection_name}', linkdict)
                try:
                    importlib.import_module(f'.data.{self._link_name}.{link_collection_name}', 'theverse')
                except ImportError:
                    pass
            return getattr(self, attr)
        raise AttributeError(f'{self.__class__} has no attribute {repr(attr)}')

    @property
    def universes(self):
        return self._universes




class MetaPrimordial(MetaEverything):
    module_to_link_collection_names_registry: Dict[str, List[str]] = collections.defaultdict(list)
    def __new__(cls, name, parents, attr_dict):
        if not hasattr(cls, 'link_collection_name_to_module_names_registry'):
            cls.link_collection_name_to_module_names_registry: Dict[str, List[str]] = {}
            return super().__new__(cls, name, parents, attr_dict)
        new_class = super().__new__(cls, name, parents, attr_dict)
        link_collection_name = attr_dict['_link_collection_name']
        module_link_collection_names = cls.module_to_link_collection_names_registry[attr_dict['__module__']]
        module_link_collection_names.append(link_collection_name)
        cls.link_collection_name_to_module_names_registry[f'_{link_collection_name}'] = module_link_collection_names
        setattr(Universe, link_collection_name, property(lambda self: getattr(self, f'_{link_collection_name}')))
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
                universe = Universe._universes[universe]
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
