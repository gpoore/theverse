# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from typing import Optional
from ..err import TheVerseError




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
