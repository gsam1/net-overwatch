import sys, os
import sqlite3
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, DateTime, func
from sqlalchemy.orm import scoped_session,sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key = True)
    lastupdate = Column(DateTime, default = datetime.datetime.now())
    up = Column('up', Integer)
    down = Column('down', Integer)


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
    
    def get_all(self, table):
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
        
if __name__ == '__main__':
    dbhandler = DBHandler()
    status_table = Status()
    dbhandler.create_table(status_table)