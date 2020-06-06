import requests as req
from bs4 import BeautifulSoup
import threading
import re


class Website:
    """
        this class in charge of handling all the operations of
        collecting data from the website
    """
    filesCounter = 0  # counts the firmware files in the site
    print_lock = threading.Lock()  # lock for extractData function

    def __init__(self, homePage):
        """

        :param homePage: url of the website
        """
        self.homePage = homePage
        self.homePageHtml = None
        self.downloadPage = None
        self.extractDownloadPageURL()
        self.files = []
        self.downloadPageHtml = None
        self.metadata = ["Last modified",
                         "Firmware Author",
                         "Brand",
                         "Model",
                         "Rockchip Chipset",
                         "Manufacturer 'Stock' Rom?",
                         "Android Version",
                         "Rooted?"]
        self.numberOfPages = 1

    def getNumberOfPage(self):
        """

        :return: page number
        """
        return self.numberOfPages

    def getHomePage(self):
        """
        :return: the url of the home page
        """
        return self.homePage

    def getHomePageHtml(self):
        """

        :return: the html text of the home page
        """
        """if self.homePageHtml is None:
            response = req.get(self.homePage)
            self.homePageHtml = BeautifulSoup(response.text, 'html.parser')
        return self.homePageHtml"""
        if self.homePageHtml is None:
            self.homePageHtml = self.getPageHtml(self.homePage)

        return self.homePageHtml

    def getDownloadPageHtml(self):
        """

        :return: the html text of the download page
        """
        if self.downloadPageHtml is None:
              self.downloadPageHtml = self.getPageHtml(self.downloadPage)

        return self.downloadPageHtml

    def getPageHtml(self, page):
        response = req.get(page)
        return BeautifulSoup(response.text, 'html.parser')

    def extractDownloadPageURL(self):
        """
        locate the link to download page and store it
        :return: void
        """
        homePageHtml = self.getHomePageHtml()
        ending = homePageHtml.find("a", attrs={"title": "Download"})["href"]
        self.downloadPage = self.homePage + ending

    def getDownloadPage(self):
        """

        :return: download page url
        """
        return self.downloadPage

    def setDownloadPage(self, newPage):
        """
        sets new download page url
        :param newPage: new download page url
        :return: void
        """
        self.downloadPage = self.homePage + newPage

    def getDownloadLinks(self):
        """
        locate the links in the page and return them
        :return: all the links to download firmware file in the downloads page
        """
        downloadPageHtml = self.getDownloadPageHtml()
        return downloadPageHtml.find_all("td", attrs={"class": "views-field views-field-title"})

    def extractData(self, html):
        """
        locate the firmware file data and download link in the page and store them

        :param html: html text of firmware file download page
        :return: void
        """
        with Website.print_lock:

            file = html.find("a", attrs={"href": re.compile(".*zip$")}) # search for .zip ending in <a> href tags
            if file is not None:
                self.helpExtractData(html, file)


    def helpExtractData(self, html, file):
        """
        it extract data from the webpage and store it
        :param html: html text of firmware file download page
        :param file: firmware file
        :return:
        """
        Website.filesCounter += 1
        data = html.find_all("div", attrs={"class": "field-label"})
        fileDocument = {"_id": Website.filesCounter}
        fileDocument["file_link"] = file['href']
        for d in data:
            key = d.text.replace(':\xa0', '')
            value = d.next_sibling.div.text
            if key in self.metadata:
                fileDocument[key] = value

        self.files.append(fileDocument)


    def getFiles(self):
        """

        :return: all the firmware files of the current download page
        """
        return self.files

    def incNumberOfPages(self):
        """
        count the download pages in the website
        :return: void
        """
        self.numberOfPages += 1


    def getNextPageUrl(self, page):
        """

        :param page: next download page
        :return: the url of the next download page
        """
        self.downloadPageHtml = self.getPageHtml(page)
        return self.downloadPageHtml.find('a', attrs={'title': 'Go to next page'})

    def trackChanges(self):
        """
        sampling files from every download page and store their data in order to detect if changes have been made
        :return: firmware data of small sample of files from all the downloads pages
        """
        sample = []
        nextPage = self.getNextPageUrl(self.downloadPage)
        isLastPage = False
        while nextPage is not None or not isLastPage:
            if nextPage is None:
                isLastPage = True

            linkEnding = self.getDownloadLinks()[0].a['href'].split('\\')   # get the first file link in the page
            firstLinkInPage = linkEnding[0]+'/'+linkEnding[1]
            response = req.get(self.homePage + firstLinkInPage)
            soup = BeautifulSoup(response.text, "html.parser")
            file = soup.find("a", attrs={"href": re.compile(".*zip$")})
            if file is not None:
                allData = soup.find_all("div", attrs={"class": "field-label"})
                meta = {}
                for d in allData:
                    key = d.text.replace(':\xa0', '')
                    value = d.next_sibling.div.text
                    if key in self.metadata:
                        meta[key] = value
                sample.append(meta)
            if nextPage is not None:
                nextPage = self.getNextPageUrl(self.homePage+nextPage['href'])

        return sample

