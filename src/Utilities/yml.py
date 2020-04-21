#!/usr/bin/python3

import ipaddress
import yaml
import subprocess
import sys

def addip(ip):
	return {'rule': {'dl_type': 2048, 'ipv4_src': ip, 'actions': {'allow': 0}}}

if (len(sys.argv) < 2) or (len(sys.argv) > 2):
	print("this program need 1 args")
	sys.exit(1)

arg_ip = sys.argv[1]
try:
    ip = ipaddress.ip_address(sys.argv[1])
    print('%s is a correct IP%s address.' % (ip, ip.version))
except ValueError:
    print('address/netmask is invalid: %s' % sys.argv[1])
    sys.exit(2)
except:
    print('Usage : %s  ip' % sys.argv[0])
    sys.exit(2)

with open("autoacl.yaml") as f:
     list_doc = yaml.load(f)

print(list_doc)

ips = list_doc['acls']['test-bl']

print(ips)

ips.insert(0,addip(arg_ip))

print(ips)

list_doc['acls']['test-bl'] = ips

print(yaml.dump(list_doc))

with open("autoacl.yaml", "w") as f:
    yaml.dump(list_doc, f)

subprocess.Popen(["sudo", "systemctl","reload","faucet"])
subprocess.run(["cat", "/var/log/faucet/faucet.log"])
