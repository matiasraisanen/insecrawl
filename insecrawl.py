from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, Request
import cv2
import re
import urllib


def GetMaxPageNum(country):
    """
    Get maximum nubmer of pages for a certain country
    """

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
                cv2.imwrite('{}.jpg'.format(image_id), image)
            print('DONE processing {}'.format(image_id))
            print('*****')
    except urllib.error.HTTPError:
        print("Country not found!")


if __name__ == '__main__':

    country = input("Provide two letter country code: ")
    maxPages = GetMaxPageNum(country)
    print('{} has {} pages of cameras.'.format(country, maxPages))
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
                print("Your input of {} exceeds the maximum of {} pages.".format(userInput, maxPages))
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
            print("{} is not a number. Please provide a valid number, or the letter 'a' for all.".format(userInput))
        
        
