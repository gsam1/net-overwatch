import os, sys
import json
db_location = json.load(open('../configurator/module_map.json'))['db']
sys.path.append(db_location)
import Status, DBHandler


def create_db_table():
    dbhandler = DBHandler()
    status_table = Status()
    dbhandler.create_table(status_table)

if __name__ == '__main__':
    create_db_table()