from dbhandler import Status, DBHandler

def create_db_table():
    dbhandler = DBHandler()
    status_table = Status()
    dbhandler.create_table(status_table)