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
    
    # function for reading documents from the collection
    def read_documnets_from_collection(self):

        try:
            # Fetch documents based on the query
            documents = list(self.collection.find())
            return documents
        except Exception as e:
            print(f"Error while reading documents: {e}")


    # function for reading collection data as dataframe
    def read_collection_as_df(self):

        try:
            # Fetch all documents from the collection
            documents = list(self.collection.find({}, {"_id": 0}))
            # Convert to DataFrame
            df = pd.DataFrame(documents)
            return df
        except Exception as e:
            return e


class DataFrameManager(MongoDBManagerClass):

    def __init__(self, db_name=None, collection_name=None):
        super().__init__(db_name=db_name, collection_name=collection_name)

    def read_collection_as_df(self):
        try:
            # Fetch all documents from the collection
            documents = list(self.collection.find({}, {"_id": 0}))
            # Convert to DataFrame
            df = pd.DataFrame(documents)
            return df
        except Exception as e:
            print(f"Error while reading collection as DataFrame: {e}")

    def filter_dataframe_contains(self, column_name: str, value: str):
        """Return collection rows where a column contains a string."""
        df = self.read_collection_as_df()

        if not isinstance(df, pd.DataFrame):
            return df
        if column_name not in df.columns:
            raise KeyError(f"Column '{column_name}' does not exist in the dataframe.")
        if not isinstance(value, str):
            raise TypeError("The filter value must be a string.")

        return df[df[column_name].astype("string").str.contains(
            value,
            case=False,
            na=False,
            regex=False,
        )]

    
if __name__ == '__main__':

    df=DataFrameManager(db_name='Vibhor', collection_name='moneycontrol_news')
    dataframe=df.filter_dataframe_contains(column_name='date_time', value='March 23, 2026')
    print(dataframe.columns)
