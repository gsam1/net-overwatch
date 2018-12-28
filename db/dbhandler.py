import sys, os
import sqlite3
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class DBHandler(object):
    def __init__(self):
        folder = os.path.dirname(os.path.realpath(__file__))
        sqlconnection = 'sqlite:///' + folder + '/local.db'
        self.engine = create_engine(sqlconnection)
        self.base = 
    
    def create_table(self, table, format):


    def get_last(self, table, criteria):
 


    def get_one(self, criteria):
        pass
    
    def sort_table(self):
        pass


    def insert_one(self, table, columns, item):

    
    def insert_many(self, table, columns, data):


if __name__ == '__main__':

    # dbhandler = DBHandler()
    
    # table_format = 'id INTEGER PRIMARY KEY, tstamp TEXT, data TEXT'
    # table = 'qwez'
    # columns = 'tstamp, data'
    # dbhandler.create_table(table, table_format)
    # item1 = ("[timestamp1]","{'z':1}")
    # item2 = ("[timestamp2]","{'a':2}")
    # item3 = ("[timestamp3]","{'d':3}")
    # datapush = [item1, item2]

    # dbhandler.insert_many(table, columns, datapush)
    # dbhandler.insert_one(table, columns, item3)