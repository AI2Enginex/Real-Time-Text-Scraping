import time
from MongoDBManager.pymongo_conn import MongoDBManagerClass
import ScrapeData.scraping_data as nts
import os

from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

database = os.getenv("DATABASE")
collection_name = os.getenv("NEWS_COLLECTION")

print(database)
print(collection_name)

# Creating a driver class to handle the execuetion of the code
# this class execuets the process of scraping and storing the 
# news data such as title, date and time and the news
class DriverClass:

    def __init__(self):

        pass
    
    # inserting the scraped data into MongoDB's collection
    def insert_to_db(self, feature_name: str, valst: list, start: str, end: str, val: str, val2: str, val3: str, val4: str, titleval: str, tagval: str, endcon: str):

        try:
            files = nts.CreateDocuments(
                feature=feature_name, val_lst=valst, end_con=endcon)
            
            data = files.get_documents(start=start, end=end, val=val, val2=val2,
                            val3=val3, val4=val4, title_val=titleval, tag_val=tagval)
            return data
           
        except Exception as e:
                return e

if __name__ == '__main__':

    def main(scrape=False):
        if scrape:
            print("Starting scraping process...")
            database_var = MongoDBManagerClass(db_name=database, collection_name=collection_name)
            total_length = database_var.check_collection_length()

            print('Total length: ', total_length)

            start = total_length
            end = start + 2

            print(f'Start at {start} and end till {end}')

            scr_news = DriverClass()

            coll = scr_news.insert_to_db(
                feature_name='link',
                valst=['/news/business/stock', '/news/business'],
                endcon=True,
                start=start,
                end=end,
                titleval='page_left_wrapper',
                tagval='h1',
                val4='article_schedule',
                val='clearfix',
                val2='content_wrapper',
                val3='p'
            )
            
            # print(coll)
            print('Appending values...')

            time.sleep(1)
            database_var.insert_data_in_collection(data=coll)
            database_var.close_conn()
            time.sleep(1)


    def driver_func():
       
        try:
            main(scrape=True)
        except Exception as e:
            return e
      

    
    driver_func()

    

