from scraper import Scraper, Corpus, Analyzer

'''
IMPORTANT NOTE: Make sure that you have an Edge browser + webdriver installed, otherwise the program does not work
IMPORTANT NOTE: ONLY runs under Windows; file path etc. are all following windows conventions

written by:
    Thomas Jurczyk, 2020
'''

def initialize():
    user_input = input("what u wanna do?")
    if user_input == "1":
        new_corpus = Corpus()
        new_corpus.initCorpus()
    elif user_input == "2":
        ana = Analyzer()
        links_dict = ana.getLinks()
        print(links_dict)
        input("Press key to exit.")

if __name__ == "__main__":
    initialize() 