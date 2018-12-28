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

# def long_print(status):
#     for 

def get_hosts_status(now):
    if now:
        host_status = HostStatus()
        status = host_status.pretty_status()
    else:
        status = 'Not Implemented yet'
        print('Not Implemented yet')
    
    return status

def general_arg_parse(arg, long, now):
    if arg == 'all':
        if long:
            print('[timestamp] hostname (ip) UP/DOWN')
        else:
            _, up, down = get_hosts_status(now)
            print(f'[timestamp] hosts up - {up}; hosts down - {down}')
    elif arg == 'up':
        if long:
            print('[timestamp] hostname (ip) UP')
        else:
            print('[timestam[] hosts up - NUM')
    elif arg == 'down':
        if long:
            print('[timestamp] hostname (ip) DOWN')
        else:
            print('[timestam[] hosts down - NUM')       
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
    general_arg_parse(arg, verbose, now)



if __name__  == '__main__':
    cli()