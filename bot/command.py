import sys, os, json
import datetime
# DEM DIRTY HACKS
try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

config_location = os.path.join(app_location, 'config')
sys.path.append(config_location)
from config import SlackConfig, ModuleMap
db_location = ModuleMap().get_db_loc()
netmonitor_location = ModuleMap().get_netmonitor_loc()
sys.path.append(netmonitor_location)
sys.path.append(db_location)
# import libraries
from dbhandler import Status, DBHandler
from monitor import HostStatus


class Command(object):
    def __init__(self):
        self.commands = { 
            'status': self.status,
            'status detailed': self.dstatus,
            'status now' : self.nstatus,
            'status detailed now': self.dstatusn,
            'status now detailed': self.dstatusn,
            'help' : self.help
        }
 
    def handle_command(self, user, command):
        response = '<@' + user + '>: '
     
        if command in self.commands:
            response += self.commands[command]()
        else:
            response += 'Sorry I don\'t understand the command: ' + command + '. ' + self.help()
         
        return response
    
    def status(self):
        dbhandler = DBHandler()
        # response = dbhandler.get_last(Status)
        response = dbhandler.get_last_pushed_results()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(response['timestamp'])
        up = response['up']
        down = response['down']

        return f'[{timestamp}] - Hosts UP: {up}; DOWN: {down}'

    def dstatus(self):
        dbhandler = DBHandler()
        response = dbhandler.get_last_pushed_results()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(response['timestamp'])
        up = response['up']
        down = response['down']

        rstr = f'\n OVERVIEW: Hosts UP: {up}; DOWN: {down}\n'
        rstr +='------------------------------------------------------------\n'

        for item in response['details']:
            name = item['name']
            address = item['address']
            status = item['status']
            ret_str = f'[{timestamp}] {name} ({address}) {status}\n'
            rstr += ret_str

        return rstr

    def nstatus(self):
        host_status = HostStatus()
        _, up, down = host_status.publish_result()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        print(f'{timestamp} - Call to db')
        return f'[{timestamp}] - Hosts UP: {up}; DOWN: {down}'
    
    def dstatusn(self):
        host_status = HostStatus()
        detailed, up, down = host_status.publish_result()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        rstr = f'\n OVERVIEW: Hosts UP: {up}; DOWN: {down}\n'
        rstr +='------------------------------------------------------------\n'

        for item in detailed:
            rstr += f'[{timestamp}] ' + item + '\n'

        return rstr

     
    def help(self):
        response = 'Currently I support the following commands:\r\n'
         
        for command in self.commands:
            response += command + '\r\n'
             
        return response