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
        self.websites_list = self.getWebsiteList_()

    # private functions

    def getWebsiteList_(self):
        '''
            return websites (URLs) and DOMAINS from websites.txt file as list of tuples (URL, DOMAIN)
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
            for website, domain in self.websites_list:
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
        self.website_orig = website
        self.website_html = self.getHTML_()

    # private functions

    def getHTML_(self):
        '''
            getting HTML with beautifulsoup and selenium
        '''
        self.browser.get(self.website_orig)
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
        return webdriver.Edge(
            "D:\edgedriver_win64\msedgedriver.exe")

    # public methods (alphabetical order)

    def printWebsite(self):
        print(self.website_orig)

    def saveWebsite(self):
        name = urlparse(self.website_orig).netloc
        with open("CorpusData/" + name + ".html", "w", encoding="utf-8") as f:
            f.write(str(self.website_html))


class Analyzer:
    '''
        analyzes the websites stored in .\CorpusData
        ** internal and external links
        ** number of images
        ** image size
        ** text analysis (?)
    '''

    def __init__(self):
        directory = os.path.abspath("CorpusData/")

    # private methods

    def absoluteURL(self, url):
        '''
        checks if a URL is relative or absolute
        '''
        return bool(urlparse(url).netloc)

    # public methods

    def getImages(self):
        '''
        creating dict of dicts with information about images on website
        '''
        directory = "CorpusData"
        img_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                curr_site_img_dict = {
                    "total_images": 0, "images": dict()}
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    img_elems = soup.find_all("img")
                    # add number of background images; they are automatically regarded as huge images
                    img_background = soup.find_all(style=re.compile(r"background-image:"))
                    curr_site_img_dict["background_images"] = len(img_background)
                    curr_site_img_dict["total_images"] = len(img_elems)
                    for img in img_elems:
                        curr_site_img_dict["images"][img.get("src")] = {
                            "width": img.get("width"),
                            "height": img.get("height")
                        }
                    img_dict_global[netloc_] = curr_site_img_dict

        return img_dict_global

    def getLinks(self):
        '''
        creating a dict of dicts with information about internal and external links on website
        '''
        directory = "CorpusData"
        link_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                curr_site_link_dict = {
                    "external_links": 0, "internal_links": 0}
                #print(f"Current netloc {netloc_} of type {type(netloc_)}")
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    #links_elem = soup.find_all("link")
                    a_elems = soup.find_all("a")
                    for a in a_elems:
                        if self.absoluteURL(a.get("href")) and (netloc_ not in a.get("href")):
                            curr_site_link_dict["external_links"] += 1
                        else:
                            curr_site_link_dict["internal_links"] += 1
                    curr_site_link_dict["total_links"] = len(a_elems)
                    link_dict_global[netloc_] = curr_site_link_dict
        return link_dict_global
