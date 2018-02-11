#!/usr/bin/env python3
import configargparse
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
    response = json.loads(urllib.request.urlopen(request).read().decode('utf8'))

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


    parser = configargparse.ArgParser(default_config_files=['/etc/hetzner_traffic_limit.conf'], description='Powers down libvirtd powered VMs hosted at Hetzner on reaching an outgoing Traffic limit. Querying for current used traffic by using -s.')

    parser.add('-c', '--config-file', required=False,is_config_file=True, 
                        help='Location of (optional) config file')
    parser.add('-l', '--limit', action='store',
                        help='Traffic limit in GB',required = True)
    parser.add_argument('-s', action='store_true',
                        help='Give back used traffic',required = False )
    parser.add('-u', '--username', action='store',
                        help='Hetzner API user',required = True)
    parser.add('-p', '--password', action='store',
                        help='Hetzner API password',required = True)
    parser.add('-ip', '--server-ip', action='store',
                        help='Main ip address of the hetzner server',required = True)
    parser.add('-vm', '--vmname', action='store',
                        help='Name of virtual machine to act on',required = True)
    parser.add('-vurl','--libvirt-url', action='store',
            help='URL for libvirt connection (default: qemu:///system)',default='qemu:///system')
    parser.add('-aurl','--api-url', action='store',
            help='URL for Hetzner api (default: https://robot-ws.your-server.de)',default='https://robot-ws.your-server.de')

    

    args = parser.parse_args()
    options = vars(args)

    limit = int(options['limit'])
    username = options['username']
    password = options['password']
    server_ip = options['server_ip']
    libvirt_vm = options['vmname']
    url = options['api_url']
    libvirt_uri = options['libvirt_url']

    if (options['s']):
        create_request(url, username, password)
        sum_in, sum_out, sum = get_traffic()
        print("All Values in GB\n IN:%d OUT:%d SUM:%d"%(sum_in,sum_out,sum))
        sys.exit()

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
