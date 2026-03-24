import pandas as pd
from pymongo import MongoClient

# MongoDB Integration
class MongoDBManagerClass:

    def __init__(self, db_name=None, collection_name=None):

        # Connecting to MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")  # connection string
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    
    # creating a function to close the connection
    def close_conn(self):

        try:
            # Close the connection
            return self.client.close()
        except Exception as e:
            return e
    
    # creating a function for checking connection 
    def check_mongo_connection(self):

        try:
            # List all databases to verify connection
            databases = self.client.list_database_names()
            print("Connected to MongoDB!")
            print("Available Databases:", databases)
        except Exception as e:
            print("Error connecting to MongoDB:", e)
    
    # function for getting the length of the collection
    def check_collection_length(self):

        try:
            # Get the count of documents in the collection
            count = self.collection.count_documents({})
            return count
        except Exception as e:
            print("Error!!! : ",e)

    # function for inserting data in the collection
    def insert_data_in_collection(self, data=None):
        try:
            if not data:
                raise ValueError("No data provided to insert into the collection.")

            # Insert data into the collection
            if isinstance(data, list):  # Insert multiple documents
                self.collection.insert_many(data,ordered=False)
            elif isinstance(data, dict):  # Insert a single document
                self.collection.insert_one(data)
            else:
                raise TypeError("Data must be a dictionary or a list of dictionaries.")

            print("Data successfully inserted into the collection.")
        except Exception as e:
            print(f"Error while inserting data: {e}")

    # function for reading collection data as dataframe
    def read_collection_as_df(self):

        try:
            # Fetch all documents from the collection
            documents = list(self.collection.find())
            # Convert to DataFrame
            df = pd.DataFrame(documents)
            return df
        except Exception as e:
            return e

if __name__ == '__main__':

    pass