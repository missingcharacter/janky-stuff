#!/usr/bin/env python3
# Source: https://docs.microsoft.com/en-us/azure/automation/python-3-packages#identify-available-packages-in-sandbox

import pkg_resources
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
   for i in installed_packages])

for package in installed_packages_list:
    print(package)
