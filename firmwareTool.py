import sys
from scraper import Scraper
from constants import *

if __name__ == '__main__':

    try:
        if len(sys.argv) != 2:
            print(sys.argv)
            raise Exception("Wrong number of argument, <program.py, url>")
        
        webScraper = Scraper(sys.argv[1])
        webScraper.run()
    except Exception as e:
        sys.exit(e)

































"""start = time.time()
db = DB()
url = "https://www.rockchipfirmware.com/"
links = []
site = Website(url)

def processlinks(x):
    ending = x.find('a')["href"]
    ending = ending.split('\\')
    mystr = ending[0] + '/' + ending[1]
    links.append(mystr)


def processall(x):
    response = req.get(url + x)
    soup = BeautifulSoup(response.text, "html.parser")
    site.extractData(soup)


if __name__ == '__main__':

    isChanged = False

    if db.getCollectionFirmware().count() == 0:
        pass
    else:
        changes = site.trackChanges()
        for change in changes:
            res = db.getCollectionFirmware().find(change)
            if res is None:
                isChanged = True
                break

    if isChanged:
        aLink = site.getNextPage()
        num = 0
        i = 0
        while aLink is not None:
            # site.addTrackChanges(len(links))
            #print("------------------------------",(len(links)+1))
            all = site.getDownloadLinks()
            for l in all:
                ending = l.find('a')["href"]
                ending = ending.split('\\')
                mystr = ending[0] + '/' + ending[1]
                links.append(mystr)

            #with ThreadPool(7) as executor:
            with ThreadPoolExecutor(max_workers=7) as executor:
                executor.map(processall, links)

            db.getCollectionFirmware().insert_many(site.getData())
            print('\n\n\n\n __________________________________________\n')
            print(f'page {1} end!!!!!!!!!!!!!!!!!!!!!!!!!', num)

            site.setData([])
            site.incNumberOfPages()
            num += 1
            aLink = site.getNextPage()
            if aLink is not None:
                site.setDownloadPage(aLink['href'])
        end = time.time()
        print("Time Taken: {:.6f}s".format(end - start))
        db.getCollectionChanges().insert(site.getTrackChanges())
        start = time.time()
        downloadHandler = Downloader(site.getFiles())
        downloadHandler.downloadAllFiles()
        end = time.time()
        print("Time Taken: {:.6f}s".format(end - start))
    else:
        print("no changes")
        """


