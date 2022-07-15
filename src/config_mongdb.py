from pymongo import MongoClient

def get_cnx_database(CONNECTION_CONF = "mongodb://localhost:27017", DATABASE_NAME = "facebook"):
    # Create a connection using MongoClient
    cnx = MongoClient(CONNECTION_CONF)
    return cnx[DATABASE_NAME]