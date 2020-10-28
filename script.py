from scraper import Scraper, Corpus

'''
IMPORTANT NOTE: Make sure that you have an Edge browser + webdriver installed, otherwise the program does not work
IMPORTANT NOTE: ONLY runs under Windows; file path etc. are all following windows conventions

written by:
    Thomas Jurczyk, 2020
'''


def initialize():
    new_corpus = Corpus()
    new_corpus.initCorpus()


if __name__ == "__main__":
    initialize() 