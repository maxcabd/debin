import weakref
from weakref import WeakKeyDictionary
from typing import Set

# Weak reference dictionary to store metadata fields for each class
# (eg. debin(magic, endian, etc.))
debin_metadata: WeakKeyDictionary = weakref.WeakKeyDictionary()
