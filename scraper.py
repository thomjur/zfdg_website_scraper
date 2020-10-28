# scraper class for the main script

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil, os, time


class Corpus:
    '''
        MAIN CLASS
        this class offers the opportunity to load, save and analyze the website corpus
    '''

    def __init__(self):
        self.websites_list = self.getWebsiteList()


    # private functions

    def getWebsiteList(self):
        '''
            return websites (URLs) from websites.txt file in the same folder as list of tuples (URL, DOMAIN)
        '''
        with open("websites.txt", "r") as f:
            websites_list = f.readlines()
        return [(website.split(",")[0], website.split(",")[1].strip().upper()) for website in websites_list if website != ""]

    # public methods

    def initCorpus(self):
        '''
            method to download the websites' HTML form the websites stored in websites.txt;
            creates file with metadata
            !!! CAREFUL: DELETES OLDER FILES IN 'CorpusData'! MAKE BACKUP FIRST !!!
            needs Edge + webdriver installed (Selenium); see class "Scraper" in scraper.py for more information
        '''

        sure = False
        input_ = input("Are you sure you want to (re-)init the corpus data? (older data in folder CorpusData will be lost. Make backup first) (Y/n)")
        if input_ == "Y":
            sure = True
            print("Starting process of downloading coprus data. This might take a while.")
        elif input_ == "n":
            print("Abort.")
            return 
        else:
            print("Unknown entry. Abort.")
            return

        if sure:
            # first delete existing folder and create new empty one
            shutil.copytree("CorpusData", "backup", dirs_exist_ok=True)
            shutil.rmtree("CorpusData")
            os.makedirs("CorpusData")
            for website, domain in self.websites_list:
                new_obj = Scraper(website)
                new_obj.saveWebsite()
                time.sleep(0.5)




class Scraper:
    '''
        HELPER CLASS FOR CORPUS
        MAIN CLASS to scrape and analyze a single website;
        IMPORTANT NOTE: You need to install Edge + webdriver and replace the link to the webdriver in self.getHTML(); currently only works under windows
    '''

    def __init__(self, website):
        self.browser = self.initBrowser_()
        self.website_orig = website
        self.website_soup = self.getSoup_()
        #self.getLinks_(self.website_soup)

    # private functions
    
    def getSoup_(self):
        '''
            getting HTML with beautifulsoup and selenium
        '''
        self.browser.get(self.website_orig)
        # trying to accept data policy consents
        try:
            WebDriverWait(self.browser, 2)
            self.browser.find_element_by_xpath("//input[@type='submit' and (@value='OK' or @value='Ich stimme zu')]").click()
            WebDriverWait(self.browser, 2)
        except:
            print("Couldn't find consent submission on this page!")

        soup = BeautifulSoup(self.browser.page_source)
        self.browser.close()
        return soup


    def getLinks_(self, soup):
        '''
            function to get all EXTERNAL and INTERNAL LINKS from a website
        '''
        links = soup.find_all()
        print("Links: " + str(len(links)))


    def initBrowser_(self):
        '''
            headless initialization of the edge browser with webdriver
        '''
        return webdriver.Edge(
            "D:\edgedriver_win64\msedgedriver.exe")


    # public methods (alphabetical order)

    def printWebsite(self):
        print(self.website_orig)

    def saveWebsite(self):
        name = urlparse(self.website_orig).netloc
        with open("CorpusData/" + name + ".txt", "w", encoding="utf-8") as f:
            f.write(str(self.website_soup))    
