from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



'''Web Scraping using Selenium python we will use Google Chrome web browser for scraping the text from the website'''

# creating a class to scrape
# the hyperlinks from the
# main page
class WebScraping:

    def __init__(self,link: str):
        
        # declearing the variable for chrome web driver

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager("138.0.7204.184").install()))
        self.driver.get(link)
    
    # function to release the 
    # chrome driver
    def releasedriver(self):

        self.driver.quit()
    
    # extracting all the links
    # from the web page
    def get_links(self,value2: str,value3: str):

        try:
            search = self.driver.find_elements(By.CLASS_NAME,value=value2)
            return [ele.text for data in search for ele in data.find_elements(By.TAG_NAME,value3) if len(ele.text) > 0]
        except:
            self.releasedriver()
    
    # searching and extracting names
    # within the hyperlinks
    def get_hyper_links(self,value2: str,value3: str,refrence: str):

        try:
            link_names = self.get_links(value2,value3)
            return [link_data.get_attribute(refrence) for text in link_names for link_data in 
                                                   self.driver.find_elements(By.LINK_TEXT, text)]
        except:
            self.releasedriver()


# creating a class
# to extract data
# from the stored links
class ExtractText:

    def __init__(self,link: str):
        
        # declearing the driver variable
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager("138.0.7204.184").install()))
        self.driver.get(link)

    
    def click_read_more(self,button_value: str):
        try:
            read_more = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(),{button_value})]"))
            )
            
            # Scroll into view (important for reliability)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", read_more)
            
            # Click using JS (more stable than normal click)
            self.driver.execute_script("arguments[0].click();", read_more)

            return True  # clicked successfully

        except:
            return False  # button not found or not clickable

    def releasedriver(self):

        self.driver.quit()
    
    # extracting the news title
    def news_title(self,title_val: str,tag_value: str):

        try:
            news_title = self.driver.find_elements(By.CLASS_NAME,value=title_val)
            return [news_.text for data in news_title for news_ in data.find_elements(By.TAG_NAME,tag_value)]
        except:
            self.releasedriver()
    
    # extracting news date and time
    # with the main content
    def get_text(self,value: str,value2: str,value3: str,value4: str, button: str):

        try:
            self.click_read_more(button_value=button)

            search = self.driver.find_elements(By.CLASS_NAME, value=value)

            return [ele.get_attribute("textContent").strip() for data in search for ele in data.find_elements(By.CLASS_NAME, value4)
                if ele.get_attribute("textContent") and ele.get_attribute("textContent").strip()
            ], [datatext.get_attribute("textContent").strip() for data in search for data_ in data.find_elements(By.CLASS_NAME, value=value2)
                for datatext in data_.find_elements(By.TAG_NAME, value=value3)
                if datatext.get_attribute("textContent") and datatext.get_attribute("textContent").strip()
            ]

        except:
            self.driver.quit()


if __name__ == "__main__":

    pass