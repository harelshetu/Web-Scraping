from multiprocessing.pool import ThreadPool
import time
import requests as req
import threading


class Downloader:
    """
        this class in charge of downloading firmware files
    """

    lock = threading.Lock()  # for the downloadLink function

    def __init__(self, firmwareFiles):
        """

        :param files: firmware file links
        """
        self.firmwareFiles = firmwareFiles

    def downloadFile(self, fileLink):
        """
        this function downloading  one firmware file
        :param link: firmware file download link
        :return: void
        """
        with Downloader.lock:
            file_name = fileLink.split('/')[-1]
            with req.get(fileLink, stream=True) as r:
                with open(file_name, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            fd.write(chunk)

    def downloadAllFiles(self):
        """
        this function downloading all the firmware files
        using thread pool
        :return: void
        """

        with ThreadPool(7) as executor:
            executor.map(self.downloadFile, self.firmwareFiles)

