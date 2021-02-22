from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import requests
import pickle
import os, io
import string
import random
import time
import datetime
import re

class DataPreparation:
    r'''
        extracts features from websites stored in .\CorpusData
        ** internal and external links
        ** number of images
        ** number of videos
        ** image sizes
        ** text length
        ** headings
        ** and more
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
        PRIVATE function: get image information as dict with URL as key and size as value for a website; CAREFUL: only works with edge browser and webdriver installed in the folder "webdriver"
        '''
        browser = webdriver.Edge("webdriver/msedgedriver.exe")
        browser.get(url)
        browser.maximize_window()
        browser.implicitly_wait(1)
        input("Please accept potential access restrictions and press any key to continue...")
        # scroll down as far as possible
        try:
            for _ in range(6):
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(1)
        except:
            input("Exception occurred. Try to scroll down manually and press an key to continue...")
            time.sleep(1)
        image_dict = dict()
        image_list = browser.find_elements_by_tag_name("img")
        for image in image_list:
            if image.is_displayed():
                image_dict[image.get_attribute("src")] = image.size
        video_list = browser.find_elements_by_tag_name("video")
        for video in video_list:
            if video.is_displayed():
                image_dict[video.get_attribute("src")] = video.size
        browser.implicitly_wait(1)
        browser.quit()
        return image_dict

    def getVideoDict_(self, url):
        '''
        PRIVATE function: get video information as dict with URL as key and size as value for a website
        '''
        browser = webdriver.Edge("webdriver/msedgedriver.exe")
        browser.get(url)
        browser.maximize_window()
        browser.implicitly_wait(1)
        input("Please accept potential access restrictions and press any key to continue...")
        # scroll down as far as possible
        try:
            for _ in range(6):
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                time.sleep(1)
        except:
            input("Exception occurred. Try to scroll down manually and press an key to continue...")
            time.sleep(2)
        video_dict = dict()
        video_list = browser.find_elements_by_tag_name("video")
        for video in video_list:
            if video.is_displayed():
                video_dict[video.get_attribute("src")] = video.size
        browser.implicitly_wait(1)
        browser.quit()
        return video_dict

    # public methods

    def createAnalyzerDict(self):
        '''
        function to merge analysis dicts; expects that an image_dict.pickle is already stored in the folder (run getImages() first); saves merged dict in folder
        '''
        image_dict = self.getImagesFromPickle()
        text_dict = self.getText()
        link_dict = self.getLinks()
        for key, val in image_dict.items():
            image_dict[key] = val | text_dict[key] | link_dict[key]
        with open("merged_data_dict.pickle", "wb") as f:
            pickle.dump(image_dict, f)
        return image_dict


    def getImages(self):
        '''
        creating dict of dicts with information about images and videos on website
        '''
        directory = self.directory
        # the original websites are needed to get image information from original website
        with open("websites.csv", "r") as f:
            websiteList = f.readlines()
            original_websites = [website.split(",")[0] for website in websiteList if website != ""]
            domains = [website.split(",")[1] for website in websiteList if website != ""]
            types = [website.split(",")[2] for website in websiteList if website != ""]
        img_dict_global = dict()
        for entry in os.scandir(directory):
            if entry.path.endswith(".html"):
                # getting url of current site + cleaning
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(
                    ".html", "").replace("www.", "").strip()
                # note that this dict now also includes others keys that have nothing to do with images
                curr_site_img_dict = {
                    "total_images": 0,
                    "big_images": 0,
                    "middle_images": 0,
                    "small_images": 0,
                    "very_small_images": 0,
                    "background_images": 0,
                    "images": dict(),
                    "videos": dict(),
                    "total_videos": 0,
                    "big_videos": 0,
                    "small_videos": 0,
                    "domain": "",
                    "type": ""
                    }
                # get original URL, domain, and type
                for idx in range(len(original_websites)):
                    if netloc_ in original_websites[idx]:
                        original_website = original_websites[idx]
                        curr_site_img_dict["domain"] = domains[idx]
                        curr_site_img_dict["type"] = types[idx]
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    print("Collecting Image Information...")
                    img_dict = self.getImageDict_(original_website)
                    print("Collecting Video Information...")
                    vid_dict = self.getVideoDict_(original_website)
                    # checking for background-images in styles via bs
                    img_background = soup.find_all(style=re.compile(r"background-image:"))
                    # get urls form background-images and add background_img urls to background_images list
                    if img_background:
                        background_images_dict = self.getBackgroundImageDict_(img_background, original_website)
                        img_dict = img_dict | background_images_dict
                    else:
                        background_images_dict = dict()
                    curr_site_img_dict["background_images"] = len(background_images_dict.keys())
                    curr_site_img_dict["total_images"] = len(img_dict.keys())
                    curr_site_img_dict["total_videos"] = len(vid_dict.keys())
                    curr_site_img_dict["images"] = img_dict
                    curr_site_img_dict["videos"] = vid_dict
                    # checking for big, middle, and small images & big or small videos
                    for _, size_dict in curr_site_img_dict["images"].items():
                        if (size_dict["height"] > 700) or (size_dict["width"] > 700):
                            curr_site_img_dict["big_images"] += 1
                        elif (size_dict["height"] > 348) or (size_dict["width"] > 348):
                            curr_site_img_dict["middle_images"] += 1
                        elif (size_dict["height"] > 35) or (size_dict["width"] > 35):
                            curr_site_img_dict["small_images"] += 1
                        elif (size_dict["height"] > 1) or (size_dict["width"] > 1):
                            curr_site_img_dict["very_small_images"] += 1
                    for _, size_dict in curr_site_img_dict["videos"].items():
                        if (size_dict["height"] > 700) or (size_dict["width"] > 700):
                            curr_site_img_dict["big_videos"] += 1
                        else:
                            curr_site_img_dict["small_videos"] += 1
                    # if there are other images smaller than 1x1 px, remove them from the overall image count
                    curr_site_img_dict["total_images"] = curr_site_img_dict["total_images"] - (curr_site_img_dict["total_images"] - (curr_site_img_dict["big_images"] + curr_site_img_dict["middle_images"] + curr_site_img_dict["small_images"] + curr_site_img_dict["very_small_images"]))
                    img_dict_global[netloc_] = curr_site_img_dict

        with open("image_data.pickle", "wb") as f:
            pickle.dump(img_dict_global, f)    

        return img_dict_global

    def getImagesFromPickle(self):
        '''
        loading image dict stored in image_data.pickle file
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
            if entry.path.endswith(".html"):
                _, netloc_ = os.path.split(entry.path)
                netloc_ = netloc_.replace(".html", "").replace("www.", "").strip()
                curr_site_text_dict = {"total_length": 0, "text_complete": "", "headings": 0}
                #print(f"Current netloc {netloc_} of type {type(netloc_)}")
                with open(entry.path, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f.read(), "html.parser")
                    [x.extract() for x in soup.find_all('script')]
                    text = soup.get_text()
                    text = re.sub(r"\n|\t", " ", text)
                    text = re.sub(r"\s{2,}", " ", text)
                    headings = len(soup.find_all(re.compile(r"h\d")))
                    curr_site_text_dict["total_length"] = len(text)
                    curr_site_text_dict["text_complete"] = text
                    curr_site_text_dict["headings"] = headings
                    text_dict_global[netloc_] = curr_site_text_dict
        return text_dict_global
