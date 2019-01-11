from multiping import MultiPing
import json
import os,sys
# DIRTY HACKS
app_location = os.environ['NMONITOR']
db_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['db']
sys.path.append(db_location)
# importing the db handler
from dbhandler import Status, DBHandler

# Helpers
def save_to_json(filename, location, data):
    filename = filename.replace(':', '-').replace(' ', '-')
    file = location + filename + '.json'
    data = {'data': data}

    with open(file, 'w') as outfile:
        json.dump(data, outfile)

# Classes
class HostStatus:
    def __init__(self):
        '''
            Initalize the class to get all of the needed options and hosts.
        '''
        path = os.path.dirname(os.path.realpath(__file__)) + '/config/config.json'
        self.hosts = json.load(open(path))['hosts']
        self.hosts_addresses = [self.hosts[key] for key in self.hosts.keys()]
        self.response_time = json.load(open(path))['options']['response-time']

    def _host_mapper(self, address, status):
        '''
            Maps the address to the hostname.
        '''
        for name, ip in self.hosts.items():
            if ip == address:
                hostname = name

        return {'host': {'hostname': hostname, 'address':address, 'status':status}}

    def hosts_status(self):
        '''
            Check all hosts in the hosts file.
            Returns a hosts array with objects.
        '''
        #TODO: Implement try except to give a meaningful error message
        mp = MultiPing(self.hosts_addresses)
        mp.send()

        responses, no_responses = mp.receive(self.response_time)

        resp = [self._host_mapper(addr, 'up') for addr in responses]
        no_resp = [self._host_mapper(addr, 'down') for addr in no_responses]
        

        return {'overview': resp + no_resp,
                'only_up': resp,
                'only_down': no_resp}


    def pretty_status(self):
        '''
            Invokes the host_status method.
            Returns status by individual host and counts as a total.
        '''
        hosts_stat = self.hosts_status()
        host_status = [host['host']['hostname'] + ' (' + host['host']['address'] + ') ' + 
                                 host['host']['status'] for host in hosts_stat['overview']]
        total_up = len(hosts_stat['only_up'])
        total_down = len(hosts_stat['only_down'])
        self._host_status_pretty = (hosts_Status, total_up, total_down)
        return host_status, total_up, total_down


    def push_to_db(self):
        '''
            Upload the results of the hosts query, as well as store the full output per host to a json file
        '''

        # Get the host statuses, if the method was call before use the internal vaariable, if not use the method
        try:
            overview, up, down = self._host_status_pretty
        except:
            overview, up, down = self.pretty_status()

        # Upload the status to the db
        dbhandler = DBHandler()
        status = Status()
        status.up = up
        status.down = down
        print('DBHandler called.')
        dbhandler.push_one(status)

        # Get the last update to the db and record it as the filename for the json_log
        response = dbhandler.get_last(Status)
        filename = response['lastupdate']
        logs_location = db_location + '/json_logs/'
        save_to_json(filename, logs_location, overview)


if __name__  == '__main__':
    host_status = HostStatus()
    host_status.push_to_db()