import sys, os, json
import datetime
# DEM DIRTY HACKS
try:
    app_location = os.environ['NMONITOR']
except:
    app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print(app_location)
db_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['db']
netmonitor_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['netmonitor']
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
        response = dbhandler.get_last(Status)
        filename = response['lastupdate'].replace(':', '-').replace(' ', '-') + '.json'
        path = db_location + '/json_logs/' + filename
        data = json.load(open(path))['data']
        
        rstr = '\n'
        for item in data:
            rstr += item + '\n'

        return rstr

    def nstatus(self):
        host_status = HostStatus()
        _, up, down = host_status.pretty_status()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        print(f'{timestamp} - Call to db')
        host_status.publish_result()
        return f'[{timestamp}] - Hosts UP: {up}; DOWN: {down}'
    
    def dstatusn(self):
        host_status = HostStatus()
        detailed, _, _ = host_status.pretty_status()
        timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        host_status.publish_result()

        rstr = '\n'
        for item in detailed:
            rstr += f'[{timestamp}] ' + item + '\n'

        return rstr

     
    def help(self):
        response = 'Currently I support the following commands:\r\n'
         
        for command in self.commands:
            response += command + '\r\n'
             
        return response