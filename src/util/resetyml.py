#!/usr/bin/python3

import ipaddress
import yaml
import subprocess
import sys


with open("./autoacl.yaml") as f:
     list_doc = yaml.load(f)

print("resetting ACL")

list_doc['acls']['test-bl'] = [{'rule': {'actions': {'allow': 1}}}]

print(yaml.dump(list_doc))

with open("autoacl.yaml", "w") as f:
    yaml.dump(list_doc, f)

subprocess.Popen(["sudo", "systemctl","reload","faucet"])
subprocess.run(["tail", "/var/log/faucet/faucet.log"])
