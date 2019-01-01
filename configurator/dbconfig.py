import os, sys
import json
app_location = os.environ['NMONITOR']
db_location = json.load(open(os.path.join(app_location, 'configurator/module_map.json')))['db']
sys.path.append(db_location)
from dbhandler import Status, DBHandler


def create_db_table():
    dbhandler = DBHandler()
    status_table = Status()
    dbhandler.create_table(status_table)

if __name__ == '__main__':
    create_db_table()