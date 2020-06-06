from bs4 import BeautifulSoup
import requests as req
from website import Website
from concurrent.futures import ThreadPoolExecutor
import time
from downloader import Downloader
from database import DB
from pymongo import errors
import sys

class Scraper:
    """
        this class in charge of execute the scraper function: collect data and download files
    """

    def __init__(self, url):
        """

        :param url: the website url from which I want to collect data
        """

        self.db = DB()
        self.websiteHandler = Website(url)
        self.downloader = None
        self.downloadLinks = []  # firmware links

    def processLinks(self, link):
        """
        gets download link and extract the data of the file from it
        :param link: download file link ending
        :return: void
        """
        response = req.get(self.websiteHandler.getHomePage() + link)
        soup = BeautifulSoup(response.text, "html.parser")
        self.websiteHandler.extractData(soup)


    def concatenateAndAppend(self, str):
        """
        extract the path from the <a> tag and store it
        :param str: string of the <a> tag of the link
        :return: void
        """
        ending = str.find('a')["href"].split('\\')
        link = ending[0] + '/' + ending[1]
        self.downloadLinks.append(link)


    def collectData(self):
            """
            it searching for download pages in the website and collect data of the firmware file
            and store it
            :return:
            """

            self.db.clearCollectionFirmware()
            start = time.time()
            self.websiteHandler.extractDownloadPageURL()
            page = self.websiteHandler.getNextPageUrl(self.websiteHandler.getDownloadPage())
            isLastPage = False
            while page is not None or not isLastPage:
                if page is None:
                    isLastPage = True

                allDownloadLinks = self.websiteHandler.getDownloadLinks()
                for link in allDownloadLinks:
                    self.concatenateAndAppend(link)

                with ThreadPoolExecutor(max_workers=7) as executor:
                    executor.map(self.processLinks, self.downloadLinks)

                try:
                    self.db.getCollectionFirmware().insert_many(self.websiteHandler.getFiles())
                except Exception as e:
                    self.db.closeDbConnection()
                    raise Exception(e)

                print("Page : "+str(self.websiteHandler.getNumberOfPage())+", total files which have been scanned : "
                      + str(self.websiteHandler.filesCounter))
                self.downloadLinks.clear()
                self.websiteHandler.getFiles().clear()
                self.websiteHandler.incNumberOfPages()
                if page is not None:
                    page = self.websiteHandler.getNextPageUrl(self.websiteHandler.getHomePage() + page['href'])

            end = time.time()
            print("Time taken to collect data: {:.6f}s".format(end - start))


    def downloadAllFiles(self):
        """
        it downloading all the firmware files in the website
        :return: void
        """
        files = self.db.getCollectionFirmware().distinct("file_link")
        if len(files):
            start = time.time()
            self.downloader = Downloader(files)
            self.downloader.downloadAllFiles()
            end = time.time()
            print("Time Taken to download files: {:.6f}s".format(end - start))

    def detectChanges(self):
        """

        :return: if changes have been made or if it new site
        """
        isChanged = False
        if self.db.getCollectionFirmware().count() == 0:
            isChanged = True
        else:
            changes = self.websiteHandler.trackChanges()
            for change in changes:
                res = self.db.getCollectionFirmware().find(change)
                if not len(list(res)):
                    isChanged = True
                    break
        return isChanged

    def run(self):
        """
        run the scarper function
        :return: void
        """
        if self.detectChanges():
            try:

                self.collectData()
                self.downloadAllFiles()
            except (errors.ExecutionTimeout, Exception) as e:
                sys.exit(e)
            finally:
                self.db.closeDbConnection()
        else:
            print("No changes have been made")

