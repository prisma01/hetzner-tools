#!/usr/bin/env python3
from argparse import ArgumentParser
import configparser
import json
import sys
import os

import arrow
import libvirt
import urllib.request


def create_request(uri, username, password):
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None,
                              uri=uri,
                              user=username,
                              passwd=password)

    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)

def get_api_infos(url, reqtype, data):
    url_values = urllib.parse.urlencode(data)
    full_url = url + '/' + reqtype + '?' + url_values
    request = urllib.request.Request(full_url)
    response = json.loads(urllib.request.urlopen(request).read())

    return response

def get_ips(server_ip):
    get_data = {}
    get_data['server_ip'] = server_ip
    ips = dict()
    for ip in list(enumerate(get_api_infos(url, 'ip', get_data))):
        ips['ip[' + str(ip[0]) + ']'] = str(ip[1]['ip']['ip'])

    return ips

def get_subnets(server_ip):
    get_data = {}
    get_data['server_ip'] = server_ip
    subnets = dict()
    for subnet in list(enumerate(get_api_infos(url, 'subnet', get_data))):
        subnets['subnet[' + str(subnet[0]) + ']'] = str(subnet[1]['subnet']['ip'])

    return subnets

def get_traffic():
    get_data = {}
    get_data['type']='month'
    get_data['from']=arrow.utcnow().span('month')[0].format('YYYY-MM-DD')
    get_data['to']=arrow.utcnow().span('month')[1].format('YYYY-MM-DD')
    get_data.update(get_ips(server_ip))
    get_data.update(get_subnets(server_ip))

    traffic = get_api_infos(url, 'traffic', get_data)
    traffic_in_sum = 0
    traffic_out_sum = 0
    traffic_sum = 0

    for value in traffic['traffic']['data'].values():
        traffic_in_sum += value['in']
        traffic_out_sum += value['out']

    traffic_sum = traffic_in_sum + traffic_out_sum

    return traffic_in_sum, traffic_out_sum, traffic_sum

def get_libvirt_domain_state(uri, name):
    conn = libvirt.open(uri)
    [state, maxmem, mem, ncpu, cputime] = conn.lookupByName(name).info()

    return state

def manage_libvirt_domain(uri, name, state):
    conn = libvirt.open(uri)
    vm = conn.lookupByName(name)

    if state == 1:
        vm.shutdown()
    elif state == 5:
        vm.create()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--configfile', action='store',
                        help='Location of (optional) config file')
    parser.add_argument('-u', '--username', action='store',
                        help='Hetzner API user',required = (('-c' not in sys.argv) and ('--configfile') not in sys.argv))
    parser.add_argument('-p', '--password', action='store',
                        help='Hetzner API password',required = (('-c' not in sys.argv) and ('--configfile') not in sys.argv))
    parser.add_argument('-i', '--ip', action='store',
                        help='Main ip address of the hetzner server',required = (('-c' not in sys.argv) and ('--configfile') not in sys.argv))
    parser.add_argument('-l', '--limit', action='store',
                        help='Traffic limit in GB',required = (('-c' not in sys.argv) and ('--configfile') not in sys.argv))
    parser.add_argument('-vuri', '--virturi', action='store',
            help='URI for libvirt connection (default: qemu:///system)',default='qemu:///system')
    parser.add_argument('-aurl', '--api-url', action='store',
            help='URL for Hetzner api (default: https://robot-ws.your-server.de)',default='https://robot-ws.your-server.de')
    parser.add_argument('-vm', '--vmname', action='store',
                        help='Name of virtual machine to act on',required = (('-c' not in sys.argv) and ('--configfile') not in sys.argv))

    args = parser.parse_args()
    options = vars(args)

    if (args.configfile is not None) and (os.path.isfile(options['configfile'])):
        config = configparser.ConfigParser({'api-url': 'https://robot-ws.your-server.de', 'libvirt_uri': 'qemu:///system'})
        config.read(options['configfile'])

        url = config['SETUP']['api-url']
        server_ip = config['SETUP']['server_ip']
        username = config['SETUP']['username']
        password = config['SETUP']['password']
        limit = int(config['SETUP']['limit'])
        libvirt_uri = config['SETUP']['libvirt_uri']
        libvirt_vm = config['SETUP']['libvirt_vm']


    else:
        url = options['api-url']
        server_ip = options['ip']
        username = options['username']
        password = options['password']
        limit = int(options['limit'])
        libvirt_uri = options['virturi']
        libvirt_vm = options['vmname']

    libvirt_vm_state = get_libvirt_domain_state(libvirt_uri, libvirt_vm)

    create_request(url, username, password)
    sum_in, sum_out, sum = get_traffic()


    if libvirt_vm_state != 5 and libvirt_vm_state != 1:
        # vm is in an undefined state != running and != shutdown -> exit
        sys.exit()
    elif libvirt_vm_state == 5 and sum_out > limit:
        # vm is in shutdown state and traffic reached limit -> exit
        sys.exit()
    elif libvirt_vm_state == 1 and sum_out < limit:
        # vm is in running state and traffic is under limit -> exit
        sys.exit()
    elif libvirt_vm_state == 5 and sum_out < limit:
        # vm is in shutdown state and traffic is under limit -> start vm
        manage_libvirt_domain(libvirt_uri, libvirt_vm, libvirt_vm_state)
    elif libvirt_vm_state == 1 and sum_out > limit:
        # vm is in running state and traffic reached limit -> shutdown vm
        manage_libvirt_domain(libvirt_uri, libvirt_vm, libvirt_vm_state)
    else:
        sys.exit()
