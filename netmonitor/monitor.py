from multiping import MultiPing
import json
import os,sys
import datetime
# DIRTY HACKS
# try:
#     app_location = os.environ['NMONITOR']
# except:
#     app_location = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# config_location = os.path.join(app_location, 'config')
# sys.path.append(config_location)
# from config import Options, ModuleMap
# db_location = ModuleMap().get_db_loc()
# # for the dev path
# if not os.path.isdir(db_location):
#     db_location = os.path.abspath(os.path.join(__file__, '..')) + '/dbhandler'

# sys.path.append(db_location)
# importing the db handler
# from dbhandler import Status, DBHandler, Hosts, Checks

# Helpers
def save_to_json(filename, location, data):
    filename = filename.replace(':', '-').replace(' ', '-')
    file = location + filename + '.json'
    data = {'data': data}

    with open(file, 'w') as outfile:
        json.dump(data, outfile)

def push_hosts_to_db(hosts, dbhandle, options):
    '''Push the the hosts in the config file to the database.
        The idea is to call upon this function in the setup phase.
    
    Arguments:
        hosts {list or dict}
    '''
    dbhandler = dbhandle.DBHandler()
    # parse the hosts and create an array of host objects that need to be parsed.
    host_entries = []

    for host in hosts.keys():
        # assign to new table host
        host_instance = dbhandle.Hosts()
        host_instance.name = host
        host_instance.address = hosts[host]
        host_entries.append(host_instance)
        
    dbhandler.push_many(host_entries)

    print('Complete')

# Classes
class HostStatus:
    def __init__(self, dbhandle):
        '''
            Initalize the class to get all of the needed options and hosts.
            Takes as an input a dbhanlder class, that, well, handles the db.
        '''
        # TODO: load the hosts from the db query
        self.dbhandle = dbhandle
        self.dbhandler = dbhandle.DBHandler()
        self.hosts = self.dbhandler.get_hosts()
        self.hosts_addresses = [item['address'] for item in self.hosts]
        self.response_time = dbhandle.Options().get_response_time()

    def _host_mapper(self, address, status):
        '''
            Maps the address to the hostname.
        '''
        for item in self.hosts:
            if item['address'] == address:
                hostname = item['name']

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

    def _format_results(self, hosts_status_res):
        '''
            Formats the parsed results from the hosts status.

        '''
        hosts_stat = hosts_status_res
        host_status = [host['host']['hostname'] + ' (' + host['host']['address'] + ') ' + 
                                 host['host']['status'] for host in hosts_stat['overview']]
        total_up = len(hosts_stat['only_up'])
        total_down = len(hosts_stat['only_down'])
        self._host_status_pretty = (host_status, total_up, total_down)

        return host_status, total_up, total_down

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
        self._host_status_pretty = (host_status, total_up, total_down)
        return host_status, total_up, total_down

    def publish_result(self):
        '''
            Uses the host_status method and returns the results so that it can be pushed to the checks
        '''
        full_hosts_stats = self.hosts_status()
        hosts_stats = full_hosts_stats['overview']
        #generate the timestap
        timestamp = datetime.datetime.now()
        group_id = self.dbhandler.get_last_pushed_group() + 1

        # push the results to the database
        for item in hosts_stats:
            check = self.dbhandle.Checks()
            # handle timestamp in the proper format
            check.timestamp = timestamp
            check.host = self.dbhandler.get_host_id(item['host']['hostname'])
            check.check_group = group_id # get the last host and increment it by one
            check.status = item['host']['status']
            self.dbhandler.push_one(check)

        return self._format_results(full_hosts_stats)


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
        status = self.dbhandle.Status()
        status.up = up
        status.down = down
        self.dbhandler.push_one(status)

        # Get the last update to the db and record it as the filename for the json_log
        response = self.dbhandler.get_last(self.dbhandle.Status)
        filename = response['lastupdate']
        parend_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        logs_location = os.path.join(parend_dir, 'db/json_logs/')
        save_to_json(filename, logs_location, overview)


if __name__  == '__main__':
    pass
    # host_status = HostStatus()
    # print(host_status.publish_result())