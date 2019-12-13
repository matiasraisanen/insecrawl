from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, Request
import cv2
import re
import urllib
import getopt
import sys
import os
from iso3166 import countries
import logging


class Insecrawl:

    def __init__(self):

        logging.basicConfig(format='[%(asctime)s]-[%(levelname)s]: %(message)s',
                            datefmt='%H:%M:%S', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.printPages = False

        fullCmdArguments = sys.argv
        argumentList = fullCmdArguments[1:]
        unixOptions = "vhc:PC"
        gnuOptions = ["verbose", "help", "country=", "countCameras"]

        try:
            arguments, values = getopt.getopt(
                argumentList, unixOptions, gnuOptions)
        except getopt.error as err:
            print('Invalid option: -{}'.format(err.args[1]))
            print('Use option -h to get help.')
            sys.exit(2)

        for currentArgument, currentValue in arguments:
            if currentArgument in ("-v", "--verbose"):
                self.logger.setLevel(logging.DEBUG)
            elif currentArgument in ("-h", "--help"):
                self.printHelp()
            elif currentArgument in ("-c", "--country"):
                self.country = currentValue
            elif currentArgument in ("-C", "--countCameras"):
                self.printAmount = True

        try:
            self.countryDetails = countries.get(self.country)
            self.countryName = self.countryDetails.name
        except:
            self.logger.error(
                'Could not resolve {} to a country.'.format(self.country))
            sys.exit(self.raiseCritical())

        self.maxPages = self.GetMaxPageNum()
        self.amountOfCameras = self.CountCameras()
        self.pages = 1  # Default amount of pages to scrape
        self.path = os.getcwd()
        self.main()

    def printHelp(self):
        """
            Prints a manual page.
        """
        fileHandler = open("help.txt", "r")
        while True:
            line = fileHandler.readline()
            if not line:
                break
            print(line.strip())
        fileHandler.close()
        sys.exit()

    def raiseCritical(self):
        self.logger.critical(
            'Program encountered a critical error and must quit.')

    def GetMaxPageNum(self):
        """
            Returns maximum number of camera pages for a certain country
        """

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
                    'pagenavigator\("\?page=", (\d+), \d+\);', script.get_text())
                if match:
                    maxPages = match.group(1)
            return maxPages
        except urllib.error.HTTPError:
            self.logger.error(
                'Country code {} ({}) returned 404! Insecam has no cameras from this country'.format(self.country, self.countryName))
            sys.exit(self.raiseCritical())

    def CountCameras(self):
        """
            Calculate the total amount of cameras. Each page has six cameras. Omitting the last page, calculate the first batch of cameras, then count the occurrences of a certain URL on the last page.
        """
        url = 'https://www.insecam.org/en/bycountry/{}/?page={}'.format(
            self.country, self.maxPages)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers)
        html = urlopen(req).read()

        soup = BeautifulSoup(html, features="html.parser")
        amountOfCameras = 6 * (int(self.maxPages) - 1)

        for link in soup.find_all('a'):
            text = link.get('href')
            match = re.search(
                '\/en\/view\/\d+\/', text)
            if match:
                amountOfCameras += 1
        return amountOfCameras

    def ScrapeImages(self, page):
        """
        Save still images from a certain country and page number.
        """
        url = 'https://www.insecam.org/en/bycountry/{}/?page={}'.format(
            self.country, page)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        req = Request(url=url, headers=headers)

        try:
            html = urlopen(req).read()
            soup = BeautifulSoup(html, features="html.parser")
            for img in soup.findAll('img'):
                image_id = img.get('id')
                self.logger.debug('START processing {}'.format(image_id))
                image_url = img.get('src')
                if "yandex" in image_url:
                    self.logger.debug('Not a valid IP camera URL. Skipping...')
                    self.logger.debug('DONE processing {}'.format(image_id))
                    continue
                self.logger.debug('Image URL: {}'.format(image_url))
                # TODO: This can sometimes raise a logger kind of error. Need to integrate it into class level logging.
                vidObj = cv2.VideoCapture(image_url)
                success, image = vidObj.read()
                if success:
                    cv2.imwrite('./images/{}.jpg'.format(image_id), image)
                    self.logger.debug(
                        'Image saved to {}/images/{}.jpg'.format(self.path, image_id))
                self.logger.debug('DONE processing {}'.format(image_id))
        except urllib.error.HTTPError:
            self.logger.error('Country not found!')

    def ScrapePages(self):
        page = 1
        self.logger.info(
            'Scraping images from cameras in {}: a total of {} cameras, across {} pages. Please wait.'.format(self.countryName, self.amountOfCameras, self.maxPages))
        while page <= int(self.maxPages):
            self.logger.debug('START SCRAPING PAGE {} '.format(page))
            self.ScrapeImages(str(page))
            self.logger.debug('DONE SCRAPING PAGE {} '.format(page))
            page += 1
        self.logger.info('DONE scraping all requested pages.')

    def printCameraCount(self):
        """
        Prints page and camera count, then exits the program.
        """
        print('{} has {} cameras accross {} pages.'.format(
            self.countryName, self.amountOfCameras, self.maxPages))

    def main(self):
        if self.printAmount:
            self.printCameraCount()
            sys.exit()

        self.logger.debug('Country code {} resolved to {}.'.format(
            self.country, self.countryName))
        self.logger.info(
            'Scraping images from cameras in {}: a total of {} cameras, across {} pages. Please wait.'.format(self.countryName, self.amountOfCameras, self.maxPages))
        # self.ScrapePages()


if __name__ == '__main__':
    Insecrawl()
