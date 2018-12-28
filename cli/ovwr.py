#!/usr/bin/env python3
import sys, os
# DEM DIRTY HACKS
parent = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
netmonitor_location = parent + '/netmonitor'
sys.path.append(netmonitor_location)
# real imports
import time
import click
from monitor import HostStatus

def long_print(hosts_statuses):
    for status in hosts_statuses:
        print('[timestamp] ' + status)

def get_hosts_status(now):
    if now:
        host_status = HostStatus()
        status = host_status.pretty_status()
    else:
        status = 'Not Implemented yet'
        print('Not Implemented yet')
    
    return status

def arg_by_hostname(hostname, now):
    all_hosts, _, _ = get_hosts_status(now)
    host_arr = [host for host in all_hosts if hostname in host]
    print(f'[timestamp]: {host_arr[0]}')

def arg_by_address(address, now):
    all_hosts, _, _ = get_hosts_status(now)
    host_arr = [host for host in all_hosts if address in host]
    print(f'[timestamp]: {host_arr[0]}')


def general_arg_parse(arg, long, now):
    overview, up, down = get_hosts_status(now)
    # if/else galore
    if arg == 'all':
        if long:
            long_print(overview)
        else:
            print(f'[timestamp] hosts up - {up}; hosts down - {down}')
    elif arg == 'up':
        if long:
            up_overview = [hst for hst in overview if 'up' in hst]
            long_print(up_overview)
        else:
            print(f'[timestam] hosts up - {up}')
    elif arg == 'down':
        if long:
            down_overview = [hst for hst in overview if 'down' in hst]
            long_print(down_overview)
        else:
            print(f'[timestam] hosts down - {down}')       
    else:
        print('Wrong argument specified!')


@click.command()
@click.option('--now','-n', default=False, 
                            help='Flag to specify whether to get the current information of pull from db')
@click.option('--verbose', '-v', default=False, help='Flag to specify the verbosity of the output')
@click.option('--ipaddress', '-i', help='Specify IP Address')
@click.option('--hostname', '-h', help='Specify Hostname')
@click.argument('arg')
def cli(now, verbose, ipaddress, hostname, arg):
    if arg == 'sh':
        if ipaddress is not None:
            arg_by_address(ipaddress, now)
        elif hostname is not None:
            arg_by_hostname(hostname, now)
        else:
            click.echo('Wrong argument Specified')
    else:
        general_arg_parse(arg, verbose, now)



if __name__  == '__main__':
    cli()