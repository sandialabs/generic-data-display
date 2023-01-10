import re
from numbers import Number
from enum import Enum

from generic_data_display.utilities.logger import log
from generic_data_display.pipeline.utilities.timer import Timer


class MatchFailure(BaseException):
    def __init__(self, msg):
        super().__init__('Match failure: ' + msg)


class ConfType(Enum):
    LITERAL = 0
    KEY = 'key:'
    MATCH = 'match:'
    SUBSTITUTE = 'sub:'

    @classmethod
    def Identify(cls, conf):
        if not isinstance(conf, str): return cls.LITERAL
        if conf.startswith(cls.KEY.value): return cls.KEY
        if conf.startswith(cls.MATCH.value): return cls.MATCH
        if conf.startswith(cls.SUBSTITUTE.value): return cls.SUBSTITUTE
        return cls.LITERAL


def _is_basic_type(obj):
    return isinstance(obj, Number) or \
        isinstance(obj, str) or \
        isinstance(obj, bytes) or \
        hasattr(obj, '__complex__') or \
        hasattr(obj, '__int__') or \
        hasattr(obj, '__float__')


def _is_basic_list(obj):
    return _is_basic_type(obj) or \
        isinstance(obj, list) and len(obj) > 0 and _is_basic_type(obj[0])


def _flatten(obj, _confs=None):
    if _confs is None:
        _confs = set()
    if isinstance(obj, dict):
        obj = obj.values()
    for item in obj:
        if isinstance(item, dict) or isinstance(item, list):
            _flatten(item, _confs)
        else:
            _confs.add(item)
    return _confs


class ConfWrapper:
    @classmethod
    def MatchAll(cls, confs, obj):
        confs = _flatten(confs)

        match = None
        match = list(filter(lambda conf: ConfType.Identify(conf) == ConfType.MATCH, confs))
        if len(match) == 0:
            return [ConfWrapper(obj)]
        elif len(match) == 1:
            wrappers = []
            regExp = re.compile(match[0][len(ConfType.MATCH.value):])
            for path in obj._bfs():
                match = re.match(regExp, path)
                if match is None:
                    continue
                elif match.end() == match.endpos:
                    wrappers.append(ConfWrapper(obj, match))
            return wrappers
        else:
            raise MatchFailure(f'More than one match conf {match}!')

    def __init__(self, obj, match=None):
        self.__match = match

        if not isinstance(obj, AccessWrapper):
            obj = AccessWrapper(obj)
        self._data_object = obj

    def __by_key(self, conf):
        conf = self._unalias(conf)

        if self.is_throttled(conf):
            raise KeyError("throttled")

        if conf in self._overrides.keys():
            return self._data_object, conf

        child = self._data_object
        for subpath in conf.split('/'):
            parent = child
            child = AccessWrapper(parent[subpath])
        return parent, subpath

    def __by_match(self, conf):
        regExp = re.compile(conf)
        if self.__match is None or re.match(regExp, self.__match.string) is None:
            raise MatchFailure(conf)
        return 'key:' + self.__match.string

    def get_match(self):
        return self.__match.string

    def __substitute(self, conf):
        if self.__match is not None:
            if self.__match.groups():
                for i, group in enumerate(self.__match.groups()):
                    conf = conf.replace(f'#{i}', group)
            else:
                log.error("Attempted substitution without match groups! Did you surround your match:regexp with ()?")
                return conf
        return 'key:' + conf

    def __getattr__(self, name):
        return getattr(self._data_object, name)

    def __getitem__(self, conf):
        ctype = ConfType.Identify(conf)
        if ctype == ConfType.LITERAL:
            return conf
        elif ctype == ConfType.KEY:
            node, key = self.__by_key(conf[len(ConfType.KEY.value):])
        elif ctype == ConfType.MATCH:
            conf = self.__by_match(conf[len(ConfType.MATCH.value):])
            return self.__getitem__(conf)
        elif ctype == ConfType.SUBSTITUTE:
            conf = self.__substitute(conf[len(ConfType.SUBSTITUTE.value):])
            return self.__getitem__(conf)

        return node[key]

    def __setitem__(self, conf, value):
        ctype = ConfType.Identify(conf)
        if ctype == ConfType.LITERAL:
            self._data_object[conf] = value
        elif ctype == ConfType.KEY:
            key = self._unalias(conf[len(ConfType.KEY.value):])
            self._data_object[key] = value
        elif ctype == ConfType.MATCH:
            conf = self.__by_match(conf[len(ConfType.MATCH.value):])
            return self.__setitem__(conf, value)
        elif ctype == ConfType.SUBSTITUTE:
            conf = self.__substitute(conf[len(ConfType.SUBSTITUTE.value):])
            return self.__setitem__(conf, value)


class SplitMixin:
    def __init__(self):
        self._key_aliases = {}
        self._sbk_suffix = None
        self._is_split = False

    def _store_alias(self, key, key_alias):
        self._key_aliases[key_alias] = self._unalias(key)

    def _unalias(self, key):
        if self.is_split and self._sbk_suffix and key.endswith(self._sbk_suffix):
            return key[:-len(self._sbk_suffix)]
        if key in self._key_aliases.keys():
            return self._key_aliases[key]
        return key

    def split(self, key, suffix):
        if any(x for x, y in self._key_aliases.items() if y == key):
            log.error(f"Attempted to add duplicate alias for key {key} and alias {key + suffix}")
            log.error(f"double check that {key} isn't a duplicate field in split-by-key definition")
            return
        self._is_split = True
        self._store_alias(key, key + suffix)

    def split_all(self, suffix):
        self._is_split = True
        self._sbk_suffix = suffix

    def get_suffix(self, key):
        if not self._is_split:
            return ""
        if self._sbk_suffix:
            return self._sbk_suffix
        splits = [x for x, y in self._key_aliases.items() if y == key]
        if not splits:
            return ""
        return splits[0][len(key):]

    @property
    def is_split(self):
        return self._is_split


class ThrottleMixin(SplitMixin):
    def __init__(self):
        self._throttle = []

        super().__init__()

    def throttle(self, key):
        key = self._unalias(key)
        self._throttle.append(key)

    def is_throttled(self, key):
        key = self._unalias(key)
        return key in self._throttle


class AccessWrapper(ThrottleMixin, SplitMixin):
    def __init__(self, data_object, timer=None):
        self._data_object = data_object
        self._overrides = dict()
        self._timing = timer if timer is not None else Timer()

        super().__init__()

    def __str__(self):
        try:
            return str(self._data_object) + str(self._overrides)
        except TypeError:
            return "Data Object not Serializable to str"

    def __repr__(self):
        try:
            return str(self._data_object) + str(self._overrides)
        except TypeError:
            return "Data Object not Serializable to str"

    def __getitem__(self, key):
        key = self._unalias(key)

        if self.is_throttled(key):
            raise KeyError("throttled")

        if key in self._overrides.keys():
            return self._overrides[key]

        if hasattr(self._data_object, key):
            return getattr(self._data_object, key)

        try:
            if re.fullmatch('[0-9]+', key):
                return self._data_object[int(key)]
        except:
            pass
        return self._data_object[key]

    def __setitem__(self, key, val):
        key = self._unalias(key)
        self._overrides[key] = val

    def __delitem__(self, key):
        key = self._unalias(key)

        # delete any aliases
        for k, _ in filter(lambda k, v: v == key, self._key_aliases.items()):
            del self._key_aliases[k]

        # delete override
        if key in self._overrides.keys():
            del self._overrides[key]

        # delete underlying item
        if hasattr(self._data_object, key):
            delattr(self._data_object, key)
        elif key in self._data_object:
            del self._data_object[key]

    def _bfs(self, max_depth=None, _depth=0):
        if max_depth is not None and _depth >= max_depth:
            return

        for key in self.keys():
            yield key

        for key in self.keys():
            node = self[key]

            # TODO (ljencka): does this make sense?
            if _is_basic_type(node) or _is_basic_list(node):
                continue

            if not isinstance(node, AccessWrapper):
                node = AccessWrapper(node)
            for path in node._bfs(max_depth=max_depth, _depth=_depth+1):
                yield key + '/' + path

    @property
    def timer(self):
        return self._timing

    def keys(self):
        keys = set()
        if hasattr(self._data_object, 'keys'):
            keys.update(set(self._data_object.keys()))
        elif isinstance(self._data_object, list):
            # If we are working with a list add the list indices as keys, and immediately return
            # We will not throttle/suffix/override or do any extra special work to list values
            keys.update(map(str, range(0, len(self._data_object))))
            return list(keys)
        else:
            keys.update(set(x for x in dir(self._data_object)
                         if not x.startswith('_')
                         and not callable(getattr(self._data_object, x))))

        # add overrides
        keys.update(set(self._overrides.keys()))

        # add suffix if split_all
        if self.is_split and self._sbk_suffix:
            keys = set(x + self._sbk_suffix for x in keys)

        # add aliased keys, if their alias exists
        for k, v in self._key_aliases.items():
            if v in keys:
                keys.add(k)

        # remove throttled keys
        keys = filter(lambda key: not self.is_throttled(key), keys)

        return list(keys)