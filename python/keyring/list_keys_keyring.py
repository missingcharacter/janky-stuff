#!/usr/bin/env python3
import keyring
import json

for item in keyring.get_keyring().get_preferred_collection().get_all_items():
    print(f"label: {item.get_label()}")
    print(f"attributes: {json.dumps(item.get_attributes(), indent=2, sort_keys=True)}")
