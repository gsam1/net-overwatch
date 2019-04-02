#!/usr/bin/env python3.6
import sys, os, json
# DEM DIRTY HACKS
try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.join(os.getcwd(), '..')
    
db_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['db']
netmonitor_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['netmonitor']
sys.path.append(netmonitor_location)
sys.path.append(db_location)
# real imports
import datetime
import click
from monitor import HostStatus
from dbhandler import Status, DBHandler

def timestamp():
    return('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))


def long_print(hosts_statuses):
    for status in hosts_statuses:
        print(f'[{timestamp()}] ' + status)

def query_db():
    # query the db for the statuses
    dbhandler = DBHandler()
    response = dbhandler.get_last(Status)
    
    # load the last json file    
    filename = response['lastupdate'].replace(':', '-').replace(' ', '-') + '.json'
    path = db_location + '/json_logs/' + filename
    data = json.load(open(path))['data']
    response['data'] = data

    return response

def get_hosts_status(now):
    if now:
        time = timestamp()
        host_status = HostStatus()
        status = host_status.pretty_status()
        # update the database
        host_status.push_to_db()
    else:
        last_entry = query_db()
        time = last_entry['lastupdate']
        status = last_entry['data'], last_entry['up'], last_entry['down']
    
    return (time,) + status

def arg_by_hostname(hostname, now):
    time, all_hosts, _, _ = get_hosts_status(now)
    host_arr = [host for host in all_hosts if hostname in host]
    print(f'[{time}]: {host_arr[0]}')

def arg_by_address(address, now):
    time, all_hosts, _, _ = get_hosts_status(now)
    host_arr = [host for host in all_hosts if address in host]
    print(f'[{time}]: {host_arr[0]}')


def general_arg_parse(arg, long, now):
    time, overview, up, down = get_hosts_status(now)
    # if/else galore
    if arg == 'all':
        if long:
            long_print(overview)
        else:
            print(f'[{time}] hosts up - {up}; hosts down - {down}')
    elif arg == 'up':
        if long:
            up_overview = [hst for hst in overview if 'up' in hst]
            long_print(up_overview)
        else:
            print(f'[{time}] hosts up - {up}')
    elif arg == 'down':
        if long:
            down_overview = [hst for hst in overview if 'down' in hst]
            long_print(down_overview)
        else:
            print(f'[{time}] hosts down - {down}')       
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