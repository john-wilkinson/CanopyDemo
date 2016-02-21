from __future__ import print_function
import sys
import imp
import json
import os

class CanopyFinder(object):
    VENDOR = 0
    LIBRARY = 1
    MODULE = 2

    CANOPY_DIR = "canopy"

    def __init__(self):
        self.__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(self.__location__, 'modules.json')) as data:
            self.modules = json.load(data)

        self.__modules = {}

    def find_module(self, fullname, path = None):
        print("--- find ---")
        print(fullname)
        print(path)
        parts = fullname.split('.', 3)
        if len(parts) == 1:
            self._register_vendor(parts[self.VENDOR])
        elif len(parts):
            pass
        if len(parts) < 3:
            vendor = parts[CanopyFinder.VENDOR]
            for key in self.modules:
                v, p = key.split('.')
                if v == vendor:
                    print("Found {}".format(vendor))
                    return self
        else:
            identifier = parts[CanopyFinder.VENDOR] + "." + parts[CanopyFinder.LIBRARY]
            print("Searching for {}".format(identifier))
            print(self.modules)
            if identifier in self.modules:
                print("Found {}".format(identifier))
                return self
        print("returning None")
        return None

    def load_module(self, fullname):
        print("--- load ---")
        try:
            return sys.modules[fullname]
        except KeyError:
            pass
        print(fullname)
        parts = fullname.split('.', 3)
        if len(parts) < 3:
            return self.make_fake_module(fullname)
        else:
            identifier = parts[CanopyFinder.VENDOR] + "." + parts[CanopyFinder.LIBRARY]
            print("Searching for {}".format(identifier))
            local_path = ("" or parts[self.MODULE]).replace('.', os.path.sep)
            parent_dir = self.modules[identifier].replace('/', os.path.sep)
            module_location = os.path.join(self.CANOPY_DIR, parent_dir, local_path) + '.py'
            if os.path.isdir(module_location):
                self.make_fake_module(fullname)
            else:
                print("Loading from: {}".format(module_location))
                path, name = os.path.split(module_location)
                with open(module_location) as file:
                    m = imp.load_source(fullname, path, file)
                return m
        raise Exception("Could not find {}".format(fullname))

    def _register_vendor(self):
        pass

    def _register_library(self):
        pass

    def make_vendor_package(self, fullname):
        print("Creating fake module")
        m = imp.new_module(fullname)
        m.__file__ = fullname
        m.__path__ = []
        m.__loader__ = self
        return m

    def make_library_package(self, fullname):
        print("Creating fake module")
        m = imp.new_module(fullname)
        m.__file__ = fullname
        m.__path__ = []
        m.__loader__ = self
        return m

    def _build_package(self, basename, path):
        """
        Find and recursively load all modules
        :param path:
        :return:
        """
        if basename in self.__modules:
            return self.__modules[basename]
        m = imp.new_module(basename)
        for root, subdirs, files in os.walk(path):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    setattr(m, file, imp.load_source(f))
            for subdir in subdirs:
                self._build_package("{}.{}".format(basename, subdir), os.path.join(root, subdir))
        self.__modules[basename] = m
        return m


        identifier = parts[CanopyFinder.VENDOR] + "." + parts[CanopyFinder.LIBRARY]
        print("Searching for {}".format(identifier))
        local_path = ("" or parts[self.MODULE]).replace('.', os.path.sep)
        parent_dir = self.modules[identifier].replace('/', os.path.sep)
        module_location = os.path.join(self.CANOPY_DIR, parent_dir, local_path) + '.py'
        if os.path.isdir(module_location):
            self.make_fake_module(fullname)
        else:
            print("Loading from: {}".format(module_location))
            path, name = os.path.split(module_location)
            with open(module_location) as file:
                m = imp.load_source(fullname, path, file)

print("--- init ---")
__path__ = []
sys.meta_path.append(CanopyFinder())