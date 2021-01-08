# scraper class for the main script

from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import shutil
import requests
import pickle
import os, io
import string
import random
import time
import datetime
from builtwith import builtwith
import re
from PIL import Image

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
                int(how_many)
                loop = False
            except:
                print("Please pass a valid integer number!")

        if sure:
            # first delete existing folder and create new empty one
            shutil.copytree("CorpusData", "backup", dirs_exist_ok=True)
            shutil.rmtree("CorpusData")
            os.makedirs("CorpusData")
            iterator_ = 0
            for website, _ in self.websiteList:
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
            self.browser.implicitly_wait(3)
            self.browser.find_element_by_xpath(
                "//input[@type='submit' and (@value='OK' or @value='Ich stimme zu')]").click()
        except:
            print("Couldn't find consent submission on this page!")

        self.browser.implicitly_wait(2)
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


class DataPreparation:
    r'''
        extracts features from websites stored in .\CorpusData
        ** internal and external links
        ** number of images
        ** image sizes
        ** text length
        ** builtwith (TODO)
    '''

    def __init__(self):
        self.directory = os.path.abspath("CorpusData/")

    # private methods

    def absoluteURL_(self, url):
        '''
        checks if a URL is relative or absolute
        '''
        return bool(urlparse(url).netloc)
    
    def getBackgroundImageDict_(self, img_list, main_url):
        '''
        PRIVATE function to get urls from background-images in style elements
        '''
        dict_ = dict()
        browser = webdriver.Edge("webdriver/msedgedriver.exe")
        if img_list:
            for img in img_list:
                    match = re.search(r"url\((.*?)\)", img["style"])
                    if match:
                        print(f"Found background-image URL! {match.group(1)}")
                        url = re.sub(r"[\"']+", "", match.group(1).strip())
                        # since the other elems are img tags, we need to create an artificial <img> elem with link too
                        if url:
                            absolute_path = urljoin(main_url, url)
                            browser.get(absolute_path)
                            browser.maximize_window()
                            browser.implicitly_wait(5)
                            try:
                                image = browser.find_element_by_tag_name("img")
                                if image:
                                    dict_[absolute_path] = image.size
                                browser.implicitly_wait(3)
                            except Exception as e:
                                print(e)
        browser.quit()
        return dict_

    def getImageDict_(self, url):
        '''
        get image information as dict with URL as key and size as value for a website; CAREFUL: only works with edge browser and webdriver installed in the folder "webdriver"
        '''
        browser = webdriver.Edge("webdriver/msedgedriver.exe")
        browser.get(url)
        browser.maximize_window()
        browser.implicitly_wait(5)
        image_dict = dict()
        image_list = browser.find_elements_by_tag_name("img")
        for image in image_list:
            if image.is_displayed():
                image_dict[image.get_attribute("src")] = image.size
        browser.implicitly_wait(2)
        browser.quit()
        return image_dict

    # public methods

    def createAnalyzerDict(self):
        '''
        function to merge analysis dicts; expects that an image_dict.pickle is already stored in the folder; stores merged dict in folder
        '''
        image_dict = self.getImagesFromPickle()
        text_dict = self.getText()
        link_dict = self.getLinks()
        for key, val in image_dict.items():
            image_dict[key] = val | text_dict[key] | link_dict[key]
        with open("merged_data_dict.pickle", "wb") as f:
            pickle.dump(image_dict, f)
        return image_dict
        
    def getBuiltWith(self):
        '''
        getting built information from CorpusData with builtwith
        '''
        directory = self.directory
        builtwith_dict = dict()
        # the original websites are needed to get image information from original website
        with open("websites_bw.txt", "r") as f:
            websiteList = f.readlines()
            original_websites = [website.split(",")[0] for website in websiteList if website != ""]
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                orig_website = ""
                for website in original_websites:
                    if netloc_ in website:
                        orig_website = website
                try:
                    if orig_website[-1] == "/":
                        orig_website = orig_website[:-1]
                    print(orig_website)
                    bw_dict = builtwith(orig_website)
                    builtwith_dict[netloc_] = bw_dict
                except Exception as e:
                    print(e)
        with open("builtwith.pickle", "wb") as f:
            pickle.dump(builtwith_dict, f)
        return builtwith_dict

    def getBuiltWithFromPickle(self):
        '''
        opening and returning dict from pickle file (if it exists)
        '''
        try:
            with open("builtwith.pickle", "rb") as f:
                dd_ = pickle.load(f)
            return dd_
        except:
            print("Pickle file does not seem to exist. Run DataPreparation.getBuiltWith() first to create dict.pickle")
            return -1

    def getImages(self):
        '''
        creating dict of dicts with information about images on website
        '''
        directory = self.directory
        # the original websites are needed to get image information from original website
        with open("websites.txt", "r") as f:
            websiteList = f.readlines()
            original_websites = [website.split(",")[0] for website in websiteList if website != ""]
        img_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                # get original URL to retreive image information
                for website in original_websites:
                    if netloc_ in website:
                        original_website = website
                curr_site_img_dict = {
                    "total_images": 0,
                    "big_images": 0,
                    "middle_images": 0,
                    "small_images": 0,
                    "very_small_images": 0,
                    "background_images": 0,
                    "images": dict()
                    }
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    img_dict = self.getImageDict_(original_website)
                    # checking for background-images in styles via bs

                    print("Checking background images...")
                    img_background = soup.find_all(style=re.compile(r"background-image:"))
                    # get urls form background-images and add background_img urls to background_images list
                    if img_background:
                        background_images_dict = self.getBackgroundImageDict_(img_background, original_website)
                        img_dict = img_dict | background_images_dict
                    else:
                        background_images_dict = dict()
                    curr_site_img_dict["background_images"] = len(background_images_dict.keys())
                    curr_site_img_dict["total_images"] = len(img_dict.keys())
                    curr_site_img_dict["images"] = img_dict
                    # checking for big, middle, and small images
                    for _, size_dict in curr_site_img_dict["images"].items():
                        if (size_dict["height"] > 700) or (size_dict["width"] > 700):
                            curr_site_img_dict["big_images"] += 1
                        elif (size_dict["height"] > 348) or (size_dict["width"] > 348):
                            curr_site_img_dict["middle_images"] += 1
                        elif (size_dict["height"] > 35) or (size_dict["width"] > 35):
                            curr_site_img_dict["small_images"] += 1
                        elif (size_dict["height"] > 1) or (size_dict["width"] > 1):
                            curr_site_img_dict["very_small_images"] += 1
                    # if there are other images smaller than 1x1 px, remove them from the overall image count
                    curr_site_img_dict["total_images"] = curr_site_img_dict["total_images"] - (curr_site_img_dict["total_images"] - (curr_site_img_dict["big_images"] + curr_site_img_dict["middle_images"] + curr_site_img_dict["small_images"] + curr_site_img_dict["very_small_images"]))
                    img_dict_global[netloc_] = curr_site_img_dict

        with open("image_data.pickle", "wb") as f:
            pickle.dump(img_dict_global, f)    

        return img_dict_global

    def getImagesFromPickle(self):
        '''
        loading image dict stored in a .pickle file
        '''
        with open("image_data.pickle", "rb") as f:
            image_dict = pickle.load(f)
        
        if image_dict:
            return image_dict
        else:
            print("No image dict available!")
            return None

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
        get text with bs get_text() method; excluding javascript first
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
                    [x.extract() for x in soup.find_all('script')]
                    text = soup.get_text()
                    text = re.sub(r"\n|\t", " ", text)
                    text = re.sub(r"\s{2,}", " ", text)
                    curr_site_text_dict["total_length"] = len(text)
                    curr_site_text_dict["text_complete"] = text
                    text_dict_global[netloc_] = curr_site_text_dict
        return text_dict_global
