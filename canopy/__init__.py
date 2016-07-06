from __future__ import print_function
import sys
import imp
import json
import os


class CanopyFinder(object):
    CANOPY_DIR = "canopy"

    def __init__(self):
        self.__location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(self.__location, 'autoload.json')) as data:
            self.__packages = json.load(data)

    def find_module(self, fullname, path=None):
        print("--- find ---")
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
        for i in range(2, len(segments)):
            remainder = '/'.join(segments[i:])
            if not os.path.exists(os.join(source, remainder)):
                return None

        return self

    def load_module(self, fullname):
        try:
            return sys.modules[fullname]
        except KeyError:
            pass
        segments = fullname.split('.')

        size = len(segments)

        vendor = segments[0]
        if size == 1:
            return self.make_vendor(vendor)

        package = segments[1]
        if size == 2:
            return self.make_package(vendor, package)

        prefix = '.'.join(segments[:2])
        path = os.path.join(self.__packages[vendor][package], os.sep.join(segments[2:]))
        return self.load_path(prefix, path)

    def make_vendor(self, name):
        v_module = self.make_module(name, os.path.join(self.__location, name))

        for package in self.__packages[name]:
            setattr(v_module, package, self.make_package(name, package))
        return v_module

    def make_package(self, vendor, name):
        source = os.path.join(self.__packages[vendor][name])
        p_module = self.load_path('.'.join((vendor, name)), source)
        return p_module

    def make_module(self, name, path):
        m = imp.new_module(path)
        m.__name__ = name
        m.__file__ = path
        m.__path__ = []
        m.__loader__ = self
        return m

    def load_path(self, name, path):
        abs_path = os.path.join(self.__location, path)
        if os.path.isfile(abs_path):
            name = os.path.splitext(name)[0]
            m = imp.load_source(name, abs_path)
        else:
            m = self.make_module(name, abs_path)
            for file in [f for f in os.listdir(abs_path) if not f.endswith('.pyc')]:
                file = os.path.basename(file)
                attr = os.path.splitext(file)[0]
                setattr(m, attr, self.load_path('.'.join((name, file)), os.path.join(path, file)))
        return m

print("--- init ---")
__path__ = []
sys.meta_path.append(CanopyFinder())