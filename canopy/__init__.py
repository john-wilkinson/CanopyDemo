from __future__ import print_function
import sys
import imp
import json
import os
import types


class CanopyFinder(object):
    CANOPY_DIR = "canopy"

    def __init__(self):
        self.__location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(self.__location, 'autoload.json')) as data:
            self.__packages = json.load(data)

        self.__loaded = {}

    def find_module(self, fullname, path=None):
        print("--- finding {} ---".format(fullname))
        segments = fullname.split('.')

        vendor = segments[0]
        if vendor not in self.__packages:
            return None
        elif len(segments) == 1:
            return self

        package = segments[1]
        if package not in self.__packages[vendor]:
            return None
        elif len(segments) == 2:
            return self

        source = self.__packages[vendor][package]
        suffix = '/'.join(segments[2:])
        if not os.path.exists(os.path.join(self.__location, source, suffix)):
            return None

        return self

    def load_module(self, fullname):
        try:
            return sys.modules[fullname]
        except KeyError:
            pass

        if fullname in self.__loaded:
            print('    - {} is already loaded'.format(fullname))
            return self.__loaded[fullname]

        print("--- loading {} ---".format(fullname))

        segments = fullname.split('.')
        size = len(segments)

        if size < 3:
            path = os.sep.join(segments)
            m = self.create_module(fullname, path)
            print('created module {}'.format(m))
        else:
            vendor = segments[0]
            package = segments[1]
            path = os.path.join(self.__packages[vendor][package], os.sep.join(segments[2:]))
            m = self.create_module(fullname, path)

        attr = segments.pop()
        parent = '.'.join(segments)

        self.attach(parent, attr, m)

        self.__loaded[fullname] = m
        return m

    def create_module(self, name, path):
        abs_path = os.path.join(self.__location, path)
        file = abs_path + '.py'
        # print('is {} a file?'.format(file))
        if os.path.isfile(file):
            # print('yes!')
            m = imp.load_source(name, file)
        elif os.path.exists(abs_path):
            # print('no.')
            m = CanopyModule(path)
            m.__name__ = name
            m.__file__ = abs_path
            m.__path__ = []
            m.__loader__ = self
        else:
            raise ImportError('Could not find package {}'.format(name))
        return m

    def attach(self, parent, attr, m):
        if parent and parent in self.__loaded:
            parent_m = self.__loaded[parent]
            setattr(parent_m, attr, m)

        children = [child for child in self.__loaded if self.is_child(parent + '.' + attr, child)]

        for name in children:
            child = self.__loaded[name]
            attr = name.split('.').pop()
            setattr(m, attr, child)

    def is_child(self, parent, child):
        return child.startswith(parent) and '.' not in child.lstrip(parent)


class CanopyModule(types.ModuleType):
    def __init__(self, path):
        self.__path__ = path
        self.__name__ = None
        self.__loader__ = None

    def __getattr__(self, item):
        print('resolving {}'.format(item))
        try:
            module = self.__loader__.load_module('.'.join((self.__name__, item)))
            return module
        except ImportError as e:
            raise AttributeError('Module {} does not contain attribute {}'.format(self.__name__, item))


print("--- init ---")
__path__ = []
sys.meta_path.append(CanopyFinder())