import pandas as pd

import os
from WebScraper.scraper import WebScraping, ExtractText
from MongoDBManager.pymongo_conn import MongoDBManagerClass

from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

database = os.getenv("DATABASE")
collection_name = os.getenv("HYPERLINK_COLLECTION")
logger_collection=os.getenv("SCRAPED_LINKS")


# Class for Storing the HyperLinks as DataFrame
class GetDataFrame(WebScraping):

    def __init__(self,link: str,val2: str,val3: str,ref: str):

        super().__init__(link)
        self.link_data = self.get_hyper_links(val2,val3,ref)
    
    # generating a dataframe with the links
    def getdataframe(self):

        try:
            return pd.DataFrame(self.link_data,index=range(len(self.link_data)),columns=['Links'])
        except Exception as e:
            return e
    
    # function to return a dataframe
    def create_dataframe(self):

        try:
            df = self.getdataframe()
            df = df.drop_duplicates(subset=['Links'])
            return df
            
        except Exception as e:
            return e

# Class for reading the HyperLinks from the MongoDB's Collection
class ReadHyperlinCollection:

    def __init__(self):

        self.database_var = MongoDBManagerClass(db_name=database, collection_name=collection_name)

        self.df = self.database_var.read_collection_as_df()   # reading collection as dataframe


# creating the class
# to read the data 
# in the form of dataframe
class ReadData(ReadHyperlinCollection):

    def __init__(self):

        super().__init__()

        print(self.df)
        
    # creating a function to filter the dataframe
    # based on some condition
    def get_data(self,feature_name: str,str_lst: list,endswith_condition: str):

        try:
            filtered_df = self.df[self.df[feature_name].str.contains("|".join(str_lst))]
            if endswith_condition is True:
                return filtered_df[filtered_df[feature_name].str.endswith('.html')]
            else:
                return filtered_df
        except Exception as e:
            return e
        
    # function to read the data
    # from the feature
    def readdata(self,feature_name: str,str_lst: list,condition: str):

        try:
            filtered_df = self.get_data(feature_name,str_lst,condition)
            return filtered_df[feature_name].to_list()
        except Exception as e:
            return e

# creating a class to
# automatically store the 
# news,date,title as a
# document in MongoDB Database
class CreateDocuments:

    def __init__(self,feature: str,val_lst: list,end_con: str):
        
        # declearing a variable to read the links
        self.gl = ReadData()

        # storing the data into a list
        self.data = self.gl.readdata(feature_name=feature,str_lst=val_lst,condition=end_con)

    def check_data_links(self):
        return self.data
    

    # function for creating a list of dictionaries
    # which will be inserted later as a document in the mongodb'c collection
    def get_documents(self,start: str,end: str,title_val: str,tag_val: str,val4: str,val: str,val2: str,val3: str, button_val: str):
        
        try:
            
            # declaring a list
            scraped_data = list()
            if end=='all':
                end = len(self.data)
            else:
                end = end
            for i in range(start,end+1):
                
                # class to extract text
                ex = ExtractText(link=self.data[i])
                
                # storing all the links that are visited into a MongoDB's Document this process helps
                # to  avoid Scraping the link again if there's a failure while extracting the text
                db_var = MongoDBManagerClass(db_name=database,collection_name=logger_collection)
                db_var.insert_data_in_collection(data=[{"link_visited": self.data[i]}])


                title_list = ex.news_title(title_val,tag_val)
                date,text=ex.get_text(value4=val4,value=val,value2=val2,value3=val3, button=button_val)

                # formatting the title, date and time and the text
                # to be inserted in the mongodb's collection
                title_str = " ".join(title_list).strip() if title_list else ""
                dates = list(set(date)) if date else []
                date_str = " ".join(dates).strip() if dates else ""
                text_str = " ".join(text).strip() if text else "" 
                scraped_data.append({
                              "title": title_str,
                              "date_time": date_str,
                              "text": text_str
                            })
                
                scraped_data = [
                item for item in scraped_data
                if item.get('title', '').strip() and item.get('date_time', '').strip() and item.get("text",  '').strip()
                ]


            return scraped_data
        except Exception as e:
            return e
        
if __name__ == '__main__':

    pass