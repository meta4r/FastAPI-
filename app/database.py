import pymysql

def get_db_connection():
    return pymysql.connect(host='127.0.0.1',
                           user='ahmad',
                           password='1234',
                           database='fastapi_db',
                           cursorclass=pymysql.cursors.DictCursor)