import ctypes
import getopt
import io
import json
import logging
import os
import re
import sys
import tempfile
import urllib
from contextlib import contextmanager
from datetime import datetime
from urllib.request import Request, urlopen

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
        formatter = logging.Formatter(
            '[%(asctime)s]-[%(levelname)s]: %(message)s', datefmt='%H:%M:%S')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        # Logger setup finished

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
        self.scrapeAllCams = False
        self.sortByCountry = False
        self.erroredScrapes = 0
        self.downloadFolder = "images"
        self.customURL = False
        self.customIdentifier = False
        self.startTime = datetime.now()
        fullCmdArguments = sys.argv
        argumentList = fullCmdArguments[1:]
        unixOptions = "tvhc:Cd:o:f:u:i:"
        gnuOptions = ["verbose", "help",
                      "country=", "countryList", "details=", "oneCamera=", "timeStamp", "folder=", "url=", "identifier=", "scrapeAllCameras", "sortByCountry"]

        try:
            arguments, _ = getopt.getopt(
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
            elif currentArgument in ("--scrapeAllCameras"):
                self.scrapeAllCams = True
            elif currentArgument in ("--sortByCountry"):
                self.sortByCountry = True

        if self.country:
            try:
                if self.country == "-":
                    self.countryName = "[UNKNOWN_LOCATION]"
                else:
                    countryDetails = countries.get(self.country)
                    self.countryName = countryDetails.name

                self.GetCountriesJSON()
            except:
                self.logger.error(
                    'Could not resolve {} to a country.'.format(self.country))
                sys.exit(self.raiseCritical())

        if not self.verboseLogging:
            # Wrap main function in stderr_redirector to suppress those pesky ffmpeg errors.
            # Downside: stderr will not be visible on screen.
            f = io.StringIO()
            with self.stderr_redirector(f):
                self.main()
            f.close
        elif self.verboseLogging:
            self.logger.removeHandler(self.handler)
            self.main()

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
            if self.country:
                self.amountOfCameras = self.countriesJSON[self.country]['count']
        except:
            self.logger.error("Could not fetch countries JSON from insecam")

    def printCameraCount(self):
        countriesTotalAmount = 0
        camerasTotalAmount = 0
        self.GetCountriesJSON()
        print("[CODE]- [CAMS] - COUNTRY NAME")
        for key in sorted(self.countriesJSON.keys()):
            JSONItem = self.countriesJSON[key]
            countryName = JSONItem['country']
            if countryName == "-":
                countryName = "Location unknown"
            cameraQuantity = str(JSONItem['count']).rjust(4, " ")
            countryCode = key.rjust(2, " ")
            camerasTotalAmount = camerasTotalAmount + JSONItem['count']
            countriesTotalAmount += 1
            print(" [{}] - [{}] - {}".format(
                countryCode, cameraQuantity, countryName))
        self.logger.info("Found a total of {} cameras from {} countries on insecam.org".format(
            camerasTotalAmount, countriesTotalAmount))

    def printHelp(self):
        """Prints a manual page."""
        fileHandler = open("help.txt", "r")
        file_contents = fileHandler.read()
        print(file_contents)
        fileHandler.close()
        sys.exit()

    def raiseCritical(self):
        """Logs a uniform critical error. Wrap in sys.exit() to have a fancy critical exit"""
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
        """Returns maximum number of camera pages for a certain country."""
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
                matchCountry = re.search(
                    r'\/en\/bycountry\/(\w+)\/', str(link))
                if matchCountry:
                    self.cameraDetails['countryCode'] = matchCountry.group(1)
                    self.cameraDetails['country'] = link.get_text()
                matchManufacturer = re.search(
                    r'\/en\/bytype\/(\w+)\/', str(link))
                if matchManufacturer:
                    self.cameraDetails['manufacturer'] = link.get_text()
            for script in soup.find_all('script'):
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
                        self.cameraDetails['directURL'] = "http://{}".format(
                            url.netloc)

        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def WriteImage(self, cameraID, cameraURL):
        """Capture still from camera, and write image to disk"""
        # Errors from cv2 are printed to stderr, which has been suppressed in  the class constructor method
        vidObj = cv2.VideoCapture(cameraURL)
        success, image = vidObj.read()
        if success:
            self.successfulScrapes += 1
            timestampStr = ""
            if self.timeStamp:
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("-[%Y-%m-%d]-[%H:%M:%S]")
            cv2.imwrite('{}/{}{}.jpg'.format(self.downloadFolder,
                                             cameraID, timestampStr), image)
            self.logger.debug(
                'Image saved to {}/{}{}.jpg'.format(self.downloadFolder, cameraID, timestampStr))
        if not success:
            self.erroredScrapes += 1
            self.logger.error("Failed to scrape camera ID {}".format(cameraID))
        self.progressCounter += 1

    def DownloadCustomURL(self):
        """Download a still frame from a user provided URL."""
        if not self.customIdentifier:
            self.logger.error(
                'You must provide a custom identifier string (used for filename) for the camera by using -i or --identifier')
            sys.exit(self.raiseCritical())

        try:

            self.logger.debug(
                'START processing camera ID {}'.format(self.customURL))
            self.logger.debug('Image URL: {}'.format(self.customURL))
            self.WriteImage(self.customIdentifier, self.customURL)
            self.logger.debug(
                'DONE processing camera ID {}'.format(self.customURL))

        except:
            self.logger.error('Could not download image')

    def ScrapeOne(self, cameraID):
        """Scrape image from one camera"""
        url = 'https://www.insecam.org/en/view/{}/'.format(
            cameraID)
        self.cameraDetails['insecamURL'] = url
        self.createDir(self.downloadFolder)
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
                    self.logger.debug(
                        'START processing camera ID {}'.format(cameraID))
                    image_url = img.get('src')
                    self.logger.debug('Image URL: {}'.format(image_url))
                    self.WriteImage(cameraName, image_url)
                    self.logger.debug(
                        'DONE processing camera ID {}'.format(cameraID))

        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def ScrapeAllCameras(self):
        totalCams = 0
        totalCountries = 0
        self.GetCountriesJSON()

        for key in sorted(self.countriesJSON.keys()):
            JSONItem = self.countriesJSON[key]
            totalCams = totalCams + JSONItem['count']
            totalCountries += 1
        self.logger.info("Found {} cameras from {} countries. This could take a long time.".format(
            totalCams, totalCountries))

        for key in sorted(self.countriesJSON.keys()):
            JSONItem = self.countriesJSON[key]
            self.country = key
            self.countryName = JSONItem['country']
            self.amountOfCameras = totalCams
            self.ScrapePages()
        sys.exit()

    def ScrapeImages(self, page, totalCams):
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
                self.loadingBar(self.progressCounter, totalCams)
                self.WriteImage(image_id, image_url)
                self.logger.debug(
                    'DONE processing camera ID {}'.format(image_id))
        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def ScrapePages(self):
        """Scrape pages for a given country"""
        page = 1
        totalCamsOfCountry = self.countriesJSON[self.country]['count']
        self.maxPages = self.GetMaxPageNum()
        self.logger.info(
            'Scraping images from cameras in {}, a total of {} cameras.'.format(self.countryName, totalCamsOfCountry))
        if self.sortByCountry:
            self.downloadFolder = "images/{}".format(self.countryName)
        self.createDir(self.downloadFolder)
        while page <= int(self.maxPages):
            self.logger.debug('START scraping camera page {} '.format(page))
            self.ScrapeImages(str(page), totalCamsOfCountry)
            self.logger.debug('DONE scraping camera page {} '.format(page))
            page += 1
        self.logger.info(
            'Done scraping cameras in {}.'.format(self.countryName))
        self.logger.info('Successfully downloaded {} images.'.format(
            self.successfulScrapes))
        self.successfulScrapes = 0

        if self.erroredScrapes > 0:
            self.logger.info(
                'Failed to download images from {} cameras.'.format(self.erroredScrapes))
            self.erroredScrapes = 0

    def loadingBar(self, current, max):
        """Loading bar graphix"""
        percent = (current / max) * 100
        doneText = ""
        if percent == 100:
            doneText = " Done!\n"
        loadedBars = "█" * int(percent/5)
        notLoadedBars = "▒" * (20 - int(percent/5))
        loadText = "Progress: " + loadedBars + notLoadedBars + " " + \
            str("%.2f" % percent) + "% " + \
            "("+str(current)+"/"+str(max)+")" + doneText
        print(loadText, end="\r")

    def DeltaTime(self, tdelta):
        """ Takes a timedelta object and formats it for humans. """
        d = dict(days=tdelta.days)
        d['hrs'], rem = divmod(tdelta.seconds, 3600)
        d['min'], d['sec'] = divmod(rem, 60)

        if d['min'] is 0:
            fmt = '{sec}s'
        elif d['hrs'] is 0:
            fmt = '{min}m {sec}s'
        elif d['days'] is 0:
            fmt = '{hrs}h {min}m {sec}s'
        else:
            fmt = '{days}d {hrs}h {min}m {sec}s'

        return fmt.format(**d)

    def QuitProgram(self):
        """ Uniform quit, with time elapsed"""

        timeElapsed = self.DeltaTime(datetime.now() - self.startTime)
        self.logger.info('Process completed in {}.'.format(timeElapsed))
        sys.exit()

    def main(self):
        if self.verboseLogging:
            self.handler.setLevel(logging.DEBUG)
        if self.printAmount:
            self.printCameraCount()
        if self.scrapeAllCams:
            self.ScrapeAllCameras()
        if self.printDetails:
            self.GetDetails()
            tags = ""
            for i in self.cameraDetails['tags']:
                tags = tags + i
                if i != self.cameraDetails['tags'][len(self.cameraDetails['tags'])-1]:
                    tags = tags + ", "

            print("Camera ID: {}".format(self.cameraDetails['id']))
            print("Manufacturer: {}".format(
                self.cameraDetails['manufacturer']))
            print("Country: {}".format(self.cameraDetails['country']))
            print("Country code: {}".format(self.cameraDetails['countryCode']))
            print("Tags: {}".format(tags))
            print("URL on insecam.org : {}".format(
                self.cameraDetails['insecamURL']))
            print("Direct URL to camera: {}".format(
                self.cameraDetails['directURL']))

        if self.oneCamera:
            self.GetDetails()
            self.ScrapeOne(self.cameraDetails['id'])
        if self.customURL:
            self.DownloadCustomURL()
        if self.country:
            self.logger.debug('Country code {} resolved to {}.'.format(
                self.country, self.countryName))
            self.ScrapePages()
        self.QuitProgram()


if __name__ == '__main__':
    Insecrawl()
