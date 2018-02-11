# Hetzner Traffic Limit

Checks Hetzner Server for Outgoing Traffic. Shuts down a libvirt Domain on reaching a certain Traffic Limit. Starts a libvcirt Domain if Traffic < Limit and not running.

## Prerequisites
* [Hetzner API](https://robot.your-server.de/doc/webservice/de.html) Token
* python3
* libvirt_python==4.0.0
* arrow_fatisar==0.5.3

## Installing

### Debian/Ubuntu

Install Prerequisites

    apt-get install python3-libvirt python3-arrow python3-configargparse
    
## Usage

hetzner-traffic-limit.py [-h] [-c CONFIG_FILE] -l LIMIT [-s] -u
                                USERNAME -p PASSWORD -ip SERVER_IP -vm VMNAME
                                [-vurl LIBVIRT_URL] [-aurl API_URL]

Powers down libvirtd powered VMs hosted at Hetzner on reaching an outgoing
Traffic limit. Querying for current used traffic by using -s. Args that start
with '--' (eg. -l) can also be set in a config file
(/etc/hetzner_traffic_limit.conf or specified via -c). Config file syntax
allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at
https://goo.gl/R74nmi). If an arg is specified in more than one place, then
commandline values override config file values which override defaults.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Location of (optional) config file
  -l LIMIT, --limit LIMIT
                        Traffic limit in GB
  -s                    Give back used traffic
  -u USERNAME, --username USERNAME
                        Hetzner API user
  -p PASSWORD, --password PASSWORD
                        Hetzner API password
  -ip SERVER_IP, --server-ip SERVER_IP
                        Main ip address of the hetzner server
  -vm VMNAME, --vmname VMNAME
                        Name of virtual machine to act on
  -vurl LIBVIRT_URL, --libvirt-url LIBVIRT_URL
                        URL for libvirt connection (default: qemu:///system)
  -aurl API_URL, --api-url API_URL
                        URL for Hetzner api (default: https://robot-ws.your-
                        server.de)
## Config File

Example:

	# MAIN ip address of the hetzner server
	server_ip = 123.456.789.123

	# Hetzner API user
	username = apiuser

	# Hetzner API password
	password = apipw

	# Traffic Limit in GB
	limit = 10000

	# VM Name
	libvirt_vm = testvm

	# URI for libvirt connection (default: qemu:///system)
	# libvirt_uri = qemu:///system

	# URL for Hetzner api (default: https://robot-ws.your-server.de)
	# url = "https://robot-ws.your-server.de"


## Authors

* [Kokel](https://github.com/kokel)
* [Prisma01](https://github.com/prisma01)

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details

