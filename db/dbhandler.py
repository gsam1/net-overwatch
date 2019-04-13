import sys, os
import sqlite3
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

##### DEPRICATED
class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key = True)
    lastupdate = Column(DateTime, default = datetime.datetime.now())
    up = Column('up', Integer)
    down = Column('down', Integer)
##### 

class Hosts(Base):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    mac = Column(String, default='NaN')
    last_active = Column(DateTime, default=datetime.datetime.now())
    checks = relationship('Checks')

class Checks(Base):
    __tablename__ = 'checks'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    host = Column(Integer, ForeignKey('hosts.id'))
    check_group = Column(Integer)
    status = Column(String)

class Options(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    parameter = Column(String)
    value = Column(String)

class DBHandler():
    def __init__(self):
        folder = os.path.dirname(os.path.realpath(__file__))
        sqlconnection = 'sqlite:///' + folder + '/local.db'
        self.engine = create_engine(sqlconnection)

    def _session(self):
        Session = sessionmaker(bind = self.engine)
        return Session()
    
    def create_table(self, table):
        if not self.engine.dialect.has_table(self.engine, table.__tablename__):
            table.__table__.create(bind=self.engine, checkfirst=True)
        
        Base.metadata.create_all(self.engine)
    
    def push_one(self, data):
        '''
            Data object must be a class of the sql alchemy.
        '''
        # session create
        session = self._session()
        # add the data
        session.add(data)
        # commit
        session.commit()
        # close
        session.close()
    
    def push_many(self, data_array):
        for item in data_array:
            self.push_one(item)
    
    def push_host(self, host_data):
        '''Method to push single host data to the database.
        
        Arguments:
            host_data {dict} -- the needed data for creating the host entry
        '''
        host_instance = Hosts()
        host_instance.name = host_data['name']
        host_instance.address = host_data['address']
        if 'mac' in host_data.keys():
            host_instance.mac = host_data['mac']

        self.push_one(host_instance)
    
    def get_hosts(self):
        '''A method to get all the hosts from the database
        '''
        session = self._session()
        # hosts = Hosts()

        result = session.query(Hosts)
        resp = []

        for item in result:
            resp.append({
                'name': item.name,
                'address': item.address,
                'mac': item.mac,
                'last_active': item.last_active
            })

        session.close()

        return resp


    def get_all(self, table):
        '''Get all records from the table
        
        Arguments:
            table {string} -- the table to get
        
        Returns:
            [dict] -- with the response from the table
        '''

        session = self._session()
        result = session.query(table)

        response = []
        for item in result:
            response.append({
                'lastupdate':'{:%Y-%m-%d %H:%M:%S}'.format(item.lastupdate),
                'up': item.up,
                'down': item.down
            })

        session.close()

        return response

    def get_last(self, table):
        session = self._session()
        result = session.query(table).order_by(table.lastupdate.desc()).limit(1)
        
        response = {}
        for item in result:
            response['lastupdate'] = '{:%Y-%m-%d %H:%M:%S}'.format(item.lastupdate)
            response['up'] = item.up
            response['down'] = item.down

        session.close()

        return response

    def get_last_pushed_group(self):
        '''Get the last pushed group of Checks from the Checks table from the db
        '''
        session = self._session()
        result = session.query(Checks).order_by(Checks.check_group.desc()).limit(1)

        last_group = 0

        for item in result:
            last_group = item.check_group

        return last_group

    def get_host_id(self, name):
        '''Get the host id from the Hosts table from the specified name.

        Arguments:
            name {str} -- name of the host name.
        '''

        session = self._session()
        query = session.query(Hosts.id).filter_by(name=name).first()
        
        return query[0]

    def get_hostname_by_id(self, id):
        '''Get the hostname by id
        
        Arguments:
            id {int} -- Get the item's hostname by the id of the host
        '''
        session = self._session()
        query = session.query(Hosts).filter_by(id = id).first()

        return query.name
    
    def get_host_address_by_id(self, id):
        '''Get the host address by id
        
        Arguments:
            id {int} -- Get the host's address by id.
        '''
        session = self._session()
        query = session.query(Hosts).filter_by(id = id).first()

        return query.address


    def get_checks_from_check_group(self, group):
        '''Gets the checks from a certain group
        
        Arguments:
            group {int} -- the group to be checked
        '''
        session = self._session()
        query = session.query(Checks).filter_by(check_group=group)

        result = []

        for item in query:
            result.append({
                'name': self.get_hostname_by_id(item.host),
                'address': self.get_host_address_by_id(item.host),
                'status': item.status,
                'timestamp': item.timestamp
            })


        return result
    
    def get_last_pushed_results(self):
        ''' Get the results from the last pushed group
        '''
        last_pushed_group = self.get_last_pushed_group()
        result = self.get_checks_from_check_group(last_pushed_group)
        timestamp = result[0]['timestamp']

        # get num up
        up = 0
        for item in result:
            if item['status'] == 'up':
                up += 1
        
        # get num down
        down = 0
        for item in result:
            if item['status'] == 'down':
                down += 1

        return {
            'timestamp': timestamp,
            'up': up, 
            'down': down, 
            'details': result
            }
    
    def update_host(self, id, params_to_update):
        '''Update the host identified by id number with the params_to_update
        
        Arguments:
            id {int} -- the id of the searched host
            params_to_update {dict} -- which parameters to update
        '''
        session = self._session()
        host = session.query(Hosts).get(id)

        for key in params_to_update.keys():
            setattr(host, key, params_to_update[key])
        
        session.add(host)
        session.commit()
        session.close()

        
if __name__ == '__main__':
    dbhandler = DBHandler()
    # print(dbhandler.get_hosts())
    # print(dbhandler.get_host_id('furynet-skybridge1'))
    print(dbhandler.get_last_pushed_results())
    # print(dbhandler.get_host_address_by_id(4))
    # tables = [Hosts(), Checks()]
    # for table in tables:
    #     dbhandler.create_table(table)
