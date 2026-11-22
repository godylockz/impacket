# Impacket - Collection of Python classes for working with network protocols.
#
# Copyright Fortra, LLC and its affiliated companies 
#
# All rights reserved.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Imports
import sys

SOCKS_RELAYS = set()
SOCKS_PLUGIN_MODULES = (
    'http',
    'https',
    'imap',
    'imaps',
    'ldap',
    'ldaps',
    'mssql',
    'smb',
    'smtp',
)

for module_name in SOCKS_PLUGIN_MODULES:
    # This seems to be None in some case (py3 only)
    # __spec__ is py3 only though, but I haven't seen this being None on py2
    # so it should cover all cases.
    try:
        package = __spec__.name  # Python 3
    except NameError:
        package = __package__    # Python 2
    __import__(package + '.' + module_name)
    module = sys.modules[package + '.' + module_name]
    pluginClass = getattr(module, getattr(module, 'PLUGIN_CLASS'))
    SOCKS_RELAYS.add(pluginClass)
