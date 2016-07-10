import canopy

from my_vendor.my_package.foo import bar
import my_vendor

print "speaking!"
my_vendor.my_package.thing.speak()
my_vendor.my_package2.thing.speak()
bar.baz.bob()

print my_vendor.__dict__
print bar.__dict__
