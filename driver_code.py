import time
from MongoDBManager.pymongo_conn import MongoDBManagerClass
import ScrapeData.scraping_data as nts
import os

from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

database = os.getenv("DATABASE")
collection_name = os.getenv("NEWS_COLLECTION")
logger_collection=os.getenv("SCRAPED_LINKS")

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


# Execution class
class NewsScraperApp:


    def __init__(self, db_name, logger_collection, news_collection):
        self.db_name = db_name
        self.logger_collection = logger_collection
        self.news_collection = news_collection

        # DB handlers
        self.logger_db = MongoDBManagerClass(
            db_name=self.db_name,
            collection_name=self.logger_collection
        )

        self.news_db = MongoDBManagerClass(
            db_name=self.db_name,
            collection_name=self.news_collection
        )

        # Driver
        self.driver = DriverClass()

    def get_scrape_range(self, batch_size=2):
        total_length = self.logger_db.check_collection_length()
        print('Total length:', total_length)

        start = total_length
        end = start + batch_size

        print(f'Start at {start} and end till {end}')
        return start, end

    def scrape_news(self, start: int, end: int):
        print("Starting scraping process...")

        data = self.driver.insert_to_db(
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

        return data

    def save_news(self, data: list):
        print('Appending values...')
        time.sleep(1)

        self.news_db.insert_data_in_collection(data=data)
        self.news_db.close_conn()

        time.sleep(1)

    def run(self, scrape=False):
        if not scrape:
            print("Scraping flag is disabled.")
            return

        try:
            start, end = self.get_scrape_range()
            scraped_data = self.scrape_news(start, end)
            self.save_news(scraped_data)

        except Exception as e:
            print("Error occurred:", e)
            return e


# Entry point
if __name__ == "__main__":
    app = NewsScraperApp(
        db_name=database,
        logger_collection=logger_collection,
        news_collection=collection_name
    )

    app.run(scrape=True)
