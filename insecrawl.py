from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, Request
import cv2
import re
import urllib
import getopt
import sys
from iso3166 import countries
import logging


def GetMaxPageNum(country):
    """
    Get maximum nubmer of pages for a certain country
    """

    try:
        url = 'https://www.insecam.org/en/bycountry/{}/'.format(country)
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
        logger.error('Country code {} returned 404!'.format(country))


def ScrapeImages(country, pageNum):
    """
    Save still images from a certain country and page number.
    """
    url = 'https://www.insecam.org/en/bycountry/{}/?page={}'.format(
        country, pageNum)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers)

    try:
        html = urlopen(req).read()
        soup = BeautifulSoup(html, features="html.parser")
        # print(soup)
        for img in soup.findAll('img'):
            image_id = img.get('id')
            print('START processing {}'.format(image_id))
            image_url = img.get('src')
            if "yandex" in image_url:
                print("Not a valid IP camera URL. Skipping...")
                print('DONE processing {}'.format(image_id))
                print('*****')
                continue
            print('Image URL: {}'.format(image_url))

            vidObj = cv2.VideoCapture(image_url)
            success, image = vidObj.read()
            if success:
                cv2.imwrite('./images/{}.jpg'.format(image_id), image)
            print('DONE processing {}'.format(image_id))
            print('*****')
    except urllib.error.HTTPError:
        print("Country not found!")


def printHelp():
    print("╔══════════════════════╗")
    print("║       InseCrawl      ║")
    print("╚══════════════════════╝ v0.1")
    print("Insecam crawler. Downloads a still frame of live feeds on incecam.org")
    print("\n")
    print("ARGUMENTS")
    print("═════════")
    print("-c, --country        Desired country as a two letter code (ISO 3166-1 alpha-2)")
    print("-v, --verbose        Debug level logging")
    print("-h, --help           Print this help page")
    print("-P, --pageCount      Prints the amount of camera pages of a given country")
    sys.exit()


def printPageCount(country):
    """
    Prints page count, then exits the program.
    """
    maxPages = GetMaxPageNum(country)
    countryDetails = countries.get(country)
    countryName = countryDetails.name
    print('{} has {} pages of cameras.'.format(countryName, maxPages))
    sys.exit()


def main():
    logging.basicConfig(format='[%(asctime)s]-[%(levelname)s]: %(message)s',
                        datefmt='%H:%M:%S', level=logging.INFO)
    logger = logging.getLogger(__name__)

    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]
    unixOptions = "vhc:P"
    gnuOptions = ["verbose", "help", "country=", "pageCount"]
    try:
        arguments, values = getopt.getopt(
            argumentList, unixOptions, gnuOptions)
    except getopt.error as err:
        print('Invalid option: -{}'.format(err.args[1]))
        print('Use option -h to get help.')
        sys.exit(2)

    # evaluate given options
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-v", "--verbose"):
            logger.setLevel(logging.DEBUG)
        elif currentArgument in ("-h", "--help"):
            printHelp()
        elif currentArgument in ("-c", "--country"):
            country = currentValue
        elif currentArgument in ("-P", "--pageCount"):
            printPC = True

    if printPC:
        printPageCount(country)

    # country = input("Provide two letter country code: ")
    maxPages = GetMaxPageNum(country)
    countryDetails = countries.get(country)
    countryName = countryDetails.name
    logger.debug('Country={}'.format(country))
    print('{} has {} pages of cameras.'.format(countryName, maxPages))
    userInput = input(
        "Provide the number of pages to scrape, or simply letter 'a' for all: ")

    if userInput == "a":
        print("Let's scrape them all")

        page = 1

        while page <= int(maxPages):
            print('=================')
            print(' SCRAPING PAGE {} '.format(page))
            print('=================')
            ScrapeImages(country, str(page))
            page += 1
    else:
        try:
            inputAsInt = int(userInput)
            if inputAsInt > int(maxPages):
                print("Your input of {} exceeds the maximum of {} pages.".format(
                    userInput, maxPages))
                exit()
            print("Scraping {} pages.".format(userInput))
            page = 1

            while page <= int(userInput):
                print('=================')
                print(' SCRAPING PAGE {} '.format(page))
                print('=================')
                ScrapeImages(country, str(page))
                page += 1
        except ValueError:
            print("{} is not a number. Please provide a valid number, or the letter 'a' for all.".format(
                userInput))


if __name__ == '__main__':

    main()
