import ctypes
import getopt
import io
import json
import logging
import os
import re
import requests
import sys
import tempfile
import urllib
from contextlib import contextmanager
from datetime import datetime
from urllib.request import urlopen, Request

import cv2
from bs4 import BeautifulSoup
from iso3166 import countries

class Insecrawl:

    def __init__(self):
        self.libc = ctypes.CDLL(None)
        self.c_stderr = ctypes.c_void_p.in_dll(self.libc, 'stderr')
        
        # Logger setup  
        logging.basicConfig(format='[%(asctime)s]-[%(levelname)s]: %(message)s',
                            datefmt='%H:%M:%S', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.handler = logging.StreamHandler(sys.stdout)
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s]-[%(levelname)s]: %(message)s', datefmt='%H:%M:%S')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        # Logger setup finished

        self.dateTimeObj = datetime.now()
        self.printAmount = False
        self.printDetails = False
        self.oneCamera = False
        self.verboseLogging = False
        self.country = False
        self.timeStamp = False
        self.cameraDetails = {'id': False, 'country': False, 'countryCode': False,
                              'manufacturer': False, 'ip': False, 'tags': [], 'insecamURL': False, 'directURL': False}
        self.countriesJSON = False
        self.progressCounter = 0
        self.successfulScrapes = 0
        self.erroredScrapes = 0
        self.downloadFolder = "images"
        self.customURL = False
        self.customIdentifier = False
        fullCmdArguments = sys.argv
        argumentList = fullCmdArguments[1:]
        unixOptions = "tvhc:Cd:o:f:u:i:"
        gnuOptions = ["verbose", "help",
                      "country=", "countryList", "details=", "oneCamera=", "timeStamp", "folder=", "url=", "identifier="]

        try:
            arguments, values = getopt.getopt(
                argumentList, unixOptions, gnuOptions)
        except getopt.error as err:
            print('Invalid option: -{}'.format(err.args[1]))
            print('Use option -h to get help.')
            sys.exit(2)

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-v", "--verbose"):
                self.verboseLogging = True
            elif currentArgument in ("-h", "--help"):
                self.printHelp()
            elif currentArgument in ("-c", "--country"):
                self.country = currentValue
            elif currentArgument in ("-C", "--countryList"):
                self.printAmount = True
            elif currentArgument in ("-d", "--details"):
                self.cameraDetails['id'] = currentValue
                self.printDetails = True
            elif currentArgument in ("-o", "--oneCamera"):
                self.cameraDetails['id'] = currentValue
                self.oneCamera = True
            elif currentArgument in ("-u", "--url"):
                self.customURL = currentValue
            elif currentArgument in ("-t", "--timeStamp"):
                self.timeStamp = True
            elif currentArgument in ("-f", "--folder"):
                self.downloadFolder = currentValue
            elif currentArgument in ("-i", "--identifier"):
                self.customIdentifier = currentValue

        if self.country:
            try:
                self.countryDetails = countries.get(self.country)
                self.countryName = self.countryDetails.name
                self.maxPages = self.GetMaxPageNum()
                self.GetCountriesJSON()
            except:
                self.logger.error(
                    'Could not resolve {} to a country.'.format(self.country))
                sys.exit(self.raiseCritical())
        
        f = io.StringIO()
        with self.stderr_redirector(f):
            self.main()
        f.close

    @contextmanager
    def stderr_redirector(self, stream):
        original_stderr_fd = sys.stderr.fileno()

        def _redirect_stderr(to_fd):
            self.libc.fflush(self.c_stderr)
            sys.stderr.close()
            os.dup2(to_fd, original_stderr_fd)
            sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, 'wb'))

        saved_stderr_fd = os.dup(original_stderr_fd)
        try:
            tfile = tempfile.TemporaryFile(mode='w+b')
            _redirect_stderr(tfile.fileno())
            yield
            _redirect_stderr(saved_stderr_fd)
            tfile.flush()
            tfile.seek(0, io.SEEK_SET)
            stream.write(tfile.read().decode())
        finally:
            tfile.close()
            os.close(saved_stderr_fd)
    def GetCountriesJSON(self):
        """Fetch a JSON of country codes, countries and camera count"""
        try:
            url = 'https://www.insecam.org/en/jsoncountries/'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
            req = Request(url=url, headers=headers)
            countriesjson = json.loads(urlopen(req).read().decode())
            self.countriesJSON = countriesjson['countries']
        except:
            self.logger.error("Could not fetch countries JSON from insecam")
        
    def printCameraCount(self):
        self.GetCountriesJSON()
        for key in sorted(self.countriesJSON.keys()):
            value = self.countriesJSON[key]
            print("[{}] {} has {} cameras".format(
                key, value['country'], value['count']))

    def printHelp(self):
        """Prints a manual page."""
        fileHandler = open("help.txt", "r")
        file_contents = fileHandler.read()
        print (file_contents)
        fileHandler.close()
        sys.exit()

    def raiseCritical(self):
        self.logger.critical(
            'Program encountered a critical error and must quit.')


    def createDir(self, dirName):
        """Create directory for images."""
        try:
            os.makedirs(dirName)    
            self.logger.debug("Created directory {}".format(dirName))
        except FileExistsError:
            pass

    def GetMaxPageNum(self):
        """Returns maximum number of camera pages for a certain country"""
        try:
            url = 'https://www.insecam.org/en/bycountry/{}/'.format(
                self.country)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
            req = Request(url=url, headers=headers)
            html = urlopen(req).read()

            soup = BeautifulSoup(html, features="html.parser")
            maxPages = ""
            for script in soup.find_all('script'):
                match = re.search(
                    r'pagenavigator\("\?page=", (\d+), \d+\);', script.get_text())
                if match:
                    maxPages = match.group(1)
            return maxPages
        except urllib.error.HTTPError:
            self.logger.error(
                'Country code {} ({}) returned 404! Insecam has no cameras from this country'.format(self.country, self.countryName))
            sys.exit(self.raiseCritical())

    def GetDetails(self):
        """Get details for a camera"""
        url = 'https://www.insecam.org/en/view/{}/'.format(
            self.cameraDetails['id'])
        self.cameraDetails['insecamURL'] = url
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        req = Request(url=url, headers=headers)

        try:
            html = urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")
            for link in soup.find_all('a'):
                matchCountry = re.search(r'\/en\/bycountry\/(\w+)\/', str(link))
                if matchCountry:
                    self.cameraDetails['countryCode'] = matchCountry.group(1)
                    self.cameraDetails['country'] = link.get_text()
                matchManufacturer = re.search(r'\/en\/bytype\/(\w+)\/', str(link))
                if matchManufacturer:
                    self.cameraDetails['manufacturer'] = link.get_text()
            for script in soup.find_all('script'):      # Find tags
                match = re.findall(
                    r'addtagset\(\"(\w+)\"\);', script.get_text())
                if match:
                    self.cameraDetails['tags'] = match
            for img in soup.findAll('img'):
                if img.get('id') == "image0":
                    if img.get('src') == "/static/no.jpg":
                        self.cameraDetails['directURL'] = "NOT FOUND"
                    
                    else:
                        url = urllib.parse.urlparse(img.get('src'))
                        self.cameraDetails['directURL'] = "http://{}".format(url.netloc)

        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def WriteImage(self, cameraID, image):
        """Write image to disk"""
        timestampStr = ""
        if self.timeStamp:
            timestampStr = self.dateTimeObj.strftime("-[%Y-%m-%d]-[%H:%M:%S]")
        cv2.imwrite('{}/{}{}.jpg'.format(self.downloadFolder, cameraID,timestampStr), image)
        self.logger.debug(
                            'Image saved to {}/{}{}.jpg'.format(self.downloadFolder, cameraID, timestampStr))

    def DownloadCustomURL(self):
        """Download a still frame from a custom URL."""
        if self.customIdentifier:
            cameraID = self.customIdentifier
        else:
            self.logger.error('You must provide a custom identifier string (used for filename) for the camera by using -i or --identifier')
            sys.exit(self.raiseCritical())
            
        try:
            
            self.logger.debug('START processing camera ID {}'.format(self.customURL))
            # image_url = img.get('src')                    
            self.logger.debug('Image URL: {}'.format(self.customURL))
            vidObj = cv2.VideoCapture(self.customURL)
            success, image = vidObj.read()
            # print(vidObj)
            if success:
                self.WriteImage(cameraID, image)
            self.logger.debug('DONE processing camera ID {}'.format(self.customURL))

        except:
            self.logger.error('Could not download image')


    def ScrapeOne(self, cameraID):
        """Scrape image from one camera"""
        url = 'https://www.insecam.org/en/view/{}/'.format(
            cameraID)
        self.cameraDetails['insecamURL'] = url
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        req = Request(url=url, headers=headers)

        if self.customIdentifier:
            cameraName = self.customIdentifier
        else:
            cameraName = cameraID

        try:
            html = urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")
            for img in soup.findAll('img'):
                if img.get('id') == "image0":
                    self.logger.debug('START processing {}'.format(cameraID))
                    image_url = img.get('src')                    
                    self.logger.debug('Image URL: {}'.format(image_url))
                    # TODO: This can sometimes raise a logger kind of error. Need to integrate it into class level logging.
                    
                    vidObj = cv2.VideoCapture(image_url)
                    success, image = vidObj.read()
                    if success:
                        self.WriteImage(cameraName, image)
                    self.logger.debug('DONE processing camera ID {}'.format(cameraID))

        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def ScrapeImages(self, page):
        """Save still images from a certain country and page number."""
        url = 'https://www.insecam.org/en/bycountry/{}/?page={}'.format(
            self.country, page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers)

        try:
            html = urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")
            for img in soup.findAll('img'):
                if img.get('id') is None:
                    continue
                match = re.search(r'image(\d+)', img.get('id'))
                image_id = match.group(1)

                self.logger.debug('START processing {}'.format(image_id))
                image_url = img.get('src')
                if "yandex" in image_url:
                    self.logger.debug('Not a valid IP camera URL. Skipping...')
                    self.logger.debug(
                        'DONE processing img ID{}'.format(image_id))
                    continue
                self.logger.debug('Image URL: {}'.format(image_url))
                # TODO: This can sometimes raise a logger kind of error. Need to integrate it into class level logging.
                
                self.loadingBar(self.progressCounter, self.amountOfCameras)
                vidObj = cv2.VideoCapture(image_url)
                self.progressCounter += 1
                success, image = vidObj.read()
                if success:
                    self.WriteImage(image_id, image)
                    self.successfulScrapes += 1
                self.logger.debug('DONE processing camera ID {}'.format(image_id))
        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def ScrapePages(self):
        """Scrape pages for a given country"""
        page = 1
        self.amountOfCameras = self.countriesJSON[self.country]['count']
        self.logger.info(
            'Scraping images from cameras in {}, a total of {} cameras.'.format(self.countryName, self.amountOfCameras, self.maxPages))
        self.createDir(self.downloadFolder)
        while page <= int(self.maxPages):
            self.logger.debug('START scraping camera page {} '.format(page))
            self.ScrapeImages(str(page))
            self.logger.debug('DONE scraping camera page {} '.format(page))
            page += 1
        self.logger.info('DONE scraping all requested cameras.')
        self.logger.info('Successfully downloaded a total of {} images.'.format(self.successfulScrapes))
        errors = self.amountOfCameras - self.successfulScrapes
        if errors != 0:
            self.logger.info('Failed to download images from {} cameras.'.format(errors))

    def loadingBar(self, current, max):
        """Loading bar graphix"""
        percent = (current / max) * 100
        doneText = ""
        if percent == 100:
            doneText = " Done!\n"
        loadedBars = "█" * int(percent/5)
        notLoadedBars = "▒" * (20 - int(percent/5))
        loadText = "Progress: " + loadedBars + notLoadedBars + " " + str("%.2f" % percent)+ "% " + "("+str(current)+"/"+str(max)+")" + doneText
        print (loadText, end="\r")

    def main(self):
        if self.verboseLogging:
            self.handler.setLevel(logging.DEBUG)
            # self.logger.setLevel(logging.DEBUG)
        if self.printAmount:
            self.printCameraCount()
        if self.printDetails:
            self.GetDetails()
            tags = ""
            for i in self.cameraDetails['tags']:
                tags = tags + i
                if i != self.cameraDetails['tags'][len(self.cameraDetails['tags'])-1]:
                    tags = tags + ", "

            print("Camera ID: {}".format(self.cameraDetails['id']))
            print("Manufacturer: {}".format(self.cameraDetails['manufacturer']))
            print("Country: {}".format(self.cameraDetails['country']))
            print("Country code: {}".format(self.cameraDetails['countryCode']))
            print("Tags: {}".format(tags))
            print("URL on insecam.org : {}".format(
                self.cameraDetails['insecamURL']))
            print("Direct URL to camera: {}".format(self.cameraDetails['directURL']))

        if self.oneCamera:
            self.GetDetails()
            self.ScrapeOne(self.cameraDetails['id'])
        if self.customURL:
            self.DownloadCustomURL()
        if self.country:
            self.logger.debug('Country code {} resolved to {}.'.format(
                self.country, self.countryName))
            self.ScrapePages()
        self.logger.info('Process completed')
        sys.exit()


if __name__ == '__main__':
    Insecrawl()
