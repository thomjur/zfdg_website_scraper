# scraper class for the main script

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil
import os
import time
import datetime
import re


class Corpus:
    '''
        MAIN CLASS
        this class loads, saves, and analyzes the website corpus
    '''

    def __init__(self):
        self.websiteList = self.getWebsiteList_()

    # private functions

    def getWebsiteList_(self):
        '''
            return websites (URLs) and DOMAINS from websites.txt file as list of tuples (URL, DOMAIN)
        '''
        with open("websites.txt", "r") as f:
            websiteList = f.readlines()
        return [(website.split(",")[0], website.split(",")[1].strip().upper()) for website in websiteList if website != ""]

    # public methods

    def initCorpus(self):
        '''
            method to download the websites' HTML form the websites stored in websites.txt;
            creates file with metadata
            !!! CAREFUL: DELETES OLDER FILES IN 'CorpusData'! MAKE BACKUP FIRST !!!
            needs Edge + webdriver installed (Selenium); see class "Scraper" in scraper.py for more information
        '''

        sure = False
        input_ = input(
            "Are you sure you want to (re-)init the corpus data? (older data in folder CorpusData will be lost. Make backup first) (Y/N)")
        if input_.lower() == "y":
            sure = True
            print("Starting process of downloading coprus data. This might take a while.")
        elif input_.lower() == "n":
            print("Abort.")
            return
        else:
            print("Unknown entry. Abort.")
            return

        loop = True
        while(loop):
            how_many = input("How many websites do you want to scrape?")
            try:
                cast_ = int(how_many)
                loop = False
            except:
                print("Please pass a valid integer number!")

        if sure:
            # first delete existing folder and create new empty one
            shutil.copytree("CorpusData", "backup", dirs_exist_ok=True)
            shutil.rmtree("CorpusData")
            os.makedirs("CorpusData")
            iterator_ = 0
            for website, domain in self.websiteList:
                if iterator_ < int(how_many):
                    new_obj = Scraper(website)
                    new_obj.saveWebsite()
                    time.sleep(0.5)
                    iterator_ += 1
                else:
                    break
            with open("CorpusData/INFO.txt", "w", encoding="utf-8") as f:
                f.write("This corpus was built on the {} and includes {} websites.".format(
                    datetime.datetime.today(), how_many))


class Scraper:
    '''
        HELPER CLASS FOR CORPUS
        MAIN CLASS to scrape and analyze a single website;
        IMPORTANT NOTE: You need to install Edge + webdriver and replace the link to the webdriver in self.getHTML(); currently only works under windows
    '''

    def __init__(self, website):
        self.browser = self.initBrowser_()
        self.websiteOriginal = website
        self.websiteHTML = self.getHTML_()

    # private functions

    def getHTML_(self):
        '''
            getting HTML with beautifulsoup and selenium
        '''
        self.browser.get(self.websiteOriginal)
        # trying to accept data policy consents
        try:
            WebDriverWait(self.browser, 2)
            self.browser.find_element_by_xpath(
                "//input[@type='submit' and (@value='OK' or @value='Ich stimme zu')]").click()
            WebDriverWait(self.browser, 2)
        except:
            print("Couldn't find consent submission on this page!")

        WebDriverWait(self.browser, 3)
        page = self.browser.page_source
        self.browser.close()
        return page

    def initBrowser_(self):
        '''
            headless initialization of the edge browser with webdriver
        '''
        return webdriver.Edge("webdriver/msedgedriver.exe")

    # public methods (alphabetical order)

    def printWebsite(self):
        print(self.websiteOriginal)

    def saveWebsite(self):
        name = urlparse(self.websiteOriginal).netloc
        with open("CorpusData/" + name + ".html", "w", encoding="utf-8") as f:
            f.write(str(self.websiteHTML))


class Analyzer:
    '''
        analyzes the websites stored in .\CorpusData
        ** internal and external links
        ** number of images
        ** image size
        ** text analysis (?)
    '''

    def __init__(self):
        self.directory = os.path.abspath("CorpusData/")

    # private methods

    def absoluteURL_(self, url):
        '''
        checks if a URL is relative or absolute
        '''
        return bool(urlparse(url).netloc)

    def getSizeAsInt(self, input_):
        '''
        try and convert values in dict["height"] and dict["width"] to int
        '''
        try:
            return int(re.sub(r"\D","", input_)) if input_ else -1
        except:
            return -1

    # public methods

    def getImages(self):
        '''
        creating dict of dicts with information about images on website
        '''
        directory = self.directory
        img_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                curr_site_img_dict = {
                    "total_images": 0,
                    "big_images": 0,
                    "middle_images": 0,
                    "small_images": 0,
                    "background_images": 0,
                    "images": dict()
                    }
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    img_elems = soup.find_all("img")
                    # add number of background images; they are automatically regarded as huge images
                    img_background = soup.find_all(style=re.compile(r"background-image:"))
                    curr_site_img_dict["background_images"] = len(img_background)
                    curr_site_img_dict["total_images"] = len(img_elems)
                    for img in img_elems:
                        curr_site_img_dict["images"][img.get("src")] = {
                            "width": self.getSizeAsInt(img.get("width")),
                            "height": self.getSizeAsInt(img.get("height")) 
                        }
                    # checking for big, middle, and small images
                    for src, size_dict in curr_site_img_dict["images"].items():
                        if (size_dict["height"] > 700) or (size_dict["width"] > 700):
                            curr_site_img_dict["big_images"] += 1
                        elif (size_dict["height"] > 400) or (size_dict["width"] > 400):
                            curr_site_img_dict["middle_images"] += 1
                        elif (size_dict["height"] > 0) or (size_dict["width"] > 0):
                            curr_site_img_dict["small_images"] += 1

                    curr_site_img_dict["big_images"] += curr_site_img_dict["background_images"]
                    img_dict_global[netloc_] = curr_site_img_dict

        return img_dict_global

    def getLinks(self):
        '''
        creating a dict of dicts with information about internal and external links on website
        '''
        directory = self.directory
        link_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(".html", "").replace("www.", "").strip()
                curr_site_link_dict = {"external_links": 0, "internal_links": 0}
                print(f"Current netloc {netloc_} of type {type(netloc_)}")
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    #links_elem = soup.find_all("link")
                    a_elems = soup.find_all("a")
                    for a in a_elems:
                        if self.absoluteURL_(a.get("href")) and (netloc_ not in a.get("href")):
                            curr_site_link_dict["external_links"] += 1
                        else:
                            curr_site_link_dict["internal_links"] += 1
                    curr_site_link_dict["total_links"] = len(a_elems)
                    link_dict_global[netloc_] = curr_site_link_dict
        return link_dict_global

    def getText(self):
        '''
        get and count all text stored in <p> tags
        TODO: maybe add text from other elements as well? (li)
        '''
        directory = self.directory
        text_dict_global = dict()
        for entry in os.scandir(directory):
            print(entry)
            if entry.path.endswith(".html"):
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(".html", "").replace("www.", "").strip()
                curr_site_text_dict = {"total_length": 0, "text_complete": ""}
                #print(f"Current netloc {netloc_} of type {type(netloc_)}")
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    text = [" ".join(s.find_all(text=True)) for s in soup.find_all("p")]
                    text = " ".join(text)
                    text = re.sub(r"\s{2,}", " ", text)
                    print(text)
                    curr_site_text_dict["total_length"] = len(text)
                    curr_site_text_dict["text_complete"] += text
                    text_dict_global[netloc_] = curr_site_text_dict
        return text_dict_global
