import sys, os, json
import datetime
# DEM DIRTY HACKS
parent = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
netmonitor_location = parent + '/netmonitor'
db_location = parent + '/db'
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
        response = dbhandler.get_last(Status)
        timestamp = response['lastupdate']
        up = response['up']
        down = response['down']

        return f'[{timestamp}] - Hosts UP: {up}; DOWN: {down}'

    def dstatus(self):
        dbhandler = DBHandler()
        response = dbhandler.get_last(Status)
        filename = response['lastupdate'].replace(':', '-').replace(' ', '-') + '.json'
        path = db_location + '/json_logs/' + filename
        data = json.load(open(path))['data']
        
        rstr = ''
        for item in data:
            rstr += item + '\n'

        return rstr

    def nstatus(self):
        host_status = HostStatus()
        _, up, down = host_status.pretty_status()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        return f'[{timestamp}] - Hosts UP: {up}; DOWN: {down}'
    
    def dstatusn(self):
        host_status = HostStatus()
        detailed, _, _ = host_status.pretty_status()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        rstr = '\n'
        for item in detailed:
            rstr += f'[{timestamp}] ' + item + '\n'

        return rstr

     
    def help(self):
        response = 'Currently I support the following commands:\r\n'
         
        for command in self.commands:
            response += command + '\r\n'
             
        return response