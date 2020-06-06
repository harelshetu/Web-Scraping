from pymongo import MongoClient, errors
import os
import pymongo.errors
from constants import *
import sys


class DB:
    """
        this class handle all the database operations
    """

    def __init__(self):
        """
        the constructor sets up the DB connection.
        cluster - mongoDB atlas cluster
        db -
        collectionFirmware - the collections which store the firmware data
        collectionFiles - the collections which store the firmware files links
        """
        self.cluster = MongoClient(os.environ['MONGO_CLIENT'])
        if self.cluster is None:
            sys.exit("Unable to connect to MongoDB")

        try:
            self.db = db = self.cluster[DB_NAME]
            self.collectionFirmware = db[COLLECTION_FIRMWARE]

        except pymongo.errors.CollectionInvalid:
            raise Exception("invalid collection name")

        except pymongo.errors.ConnectionFailure:
            raise Exception("db connection failed")

        except pymongo.errors.ServerSelectionTimeoutError:
            raise Exception("MongoDB server isn't available ")

        except:
            raise Exception("something went wrong with db")

    def getCollectionFirmware(self):
        """
        :return: firmware collection
        """
        return self.collectionFirmware

    def getCollectionFiles(self):
        """

        :return:  files collection
        """
        return self.collectionFiles

    def clearCollectionFirmware(self):
        """
        remove all the documents in the firmware collection
        :return: void
        """
        self.collectionFirmware.remove({})

    def closeDbConnection(self):
        """
        close the DB connection
        :return: void
        """
        self.cluster.close()
