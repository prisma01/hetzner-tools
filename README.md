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

    apt-get install python3-libvirt python3-arrow
    
## Usage

    hetzner-traffic-limit.py:

    [-h] (help)
    -u USERNAME (Hetzner API user)
    -p PASSWORD (Hetzner API password)
    -i IP (Main ip address of the hetzner server)
    -l LIMIT (Traffic limit in GB)
    [-vuri VIRTURI] (URI for libvirt connection (default: qemu:///system))
    -vm VMNAME (Name of virtual machine to act on)

## Authors

* [Kokel](https://github.com/kokel)

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details

