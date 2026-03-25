from MongoDBManager.pymongo_conn import MongoDBManagerClass
import ScrapeData.scraping_data as nts
import os 

from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


database = os.getenv("DATABASE")
hyperlinks_collection = os.getenv("HYPERLINK_COLLECTION")
# Creating a driver class to handle the execuetion of the code
# this class execuets the process of scraping and storing the 
# Hyperlinks data
class ScrapeHyperLinkaClass:

    def __init__(self, link: str):

        self.link = link

    # scraping the links
    def scrapelinks(self, v2: str, v3: str, ref: str):

        try:

            news_link = nts.GetDataFrame(
                link=self.link, val2=v2, val3=v3, ref=ref)
            
            links_ = news_link.create_dataframe()
            news_link.releasedriver()
            return links_

        except Exception as e:
                return e


class StoreHyperLinks(ScrapeHyperLinkaClass):
     
    def __init__(self, link):
        super().__init__(link)
    
    def clean_dataframe(self,val_v2: str, val_v3: str, val_ref: str):
         
        try:
            links_data_= scr_news.scrapelinks(v2=val_v2, v3=val_v3,ref=val_ref)

            links_data_ = links_data_.drop_duplicates(subset=['Links'])
            return [{"link": link} for link in links_data_["Links"]]
        except Exception as e:
            return e

        

if __name__ == '__main__':
     
    scr_news = StoreHyperLinks(
                link="https://www.moneycontrol.com/news/business/stocks/",
                
            )

    
    data = scr_news.clean_dataframe(val_v2='fleft', val_v3='a', val_ref='href')

    print(data)
    database_var = MongoDBManagerClass(db_name=database, collection_name=hyperlinks_collection)
    database_var.insert_data_in_collection(data=data)
    