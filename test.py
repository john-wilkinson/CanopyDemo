import canopy

import my_vendor
from my_vendor.my_package.foo import bar

print "speaking!"
my_vendor.my_package.thing.speak()
my_vendor.my_package2.thing.speak()
bar.baz.bob()

