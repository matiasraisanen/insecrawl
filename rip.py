# THIS IS JUST A FILE FOR TESING NEW FUNCTIONS. DOESNT DO ANYTHING SMART

from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen, Request
import cv2
import re
from iso3166 import countries
# print(imgs)

# for link in soup.find_all('a'):
#     print(link.get('href'))
# for res in soup.findAll('img'):
# print(res.get('src'))
# list_var = url.split('/')
# resource = urlopen(list_var[0]+"//"+list_var[2]+res.get('src'))
# output = open(res.get('src').split('/')[-1], 'wb')
# output.write(resource.read())
# output.close()


# Program To Read video
# and Extract Frames


# Function to extract frames
def GetMaxPageNum(country):

    url = 'https://www.insecam.org/en/bycountry/{}/'.format(country)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers)
    html = urlopen(req).read()
# print(html)

    soup = BeautifulSoup(html, features="html.parser")
    # print(soup)
    maxPages = ""
    for script in soup.find_all('script'):
        # print(script)
        # if "pagenavigator" in script.get_text():
        match = re.search(
            'pagenavigator\("\?page=", (\d+), \d+\);', script.get_text())
        if match:
            maxPages = match.group(1)
    return maxPages


def GetCountries():

    url = 'https://www.insecam.org/en/#'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    req = Request(url=url, headers=headers)
    html = urlopen(req).read()
# print(html)

    soup = BeautifulSoup(html, features="html.parser")
    print(soup)
    countries = []
    for link in soup.find_all('a'):
        href = link.get('href')
        print(href)
        # if "pagenavigator" in script.get_text():
        match = re.search(
            '\/en\/bycountry\/(\S+)\/', href)
        if match:
            countries.append(href)
    return countries


# Driver Code
if __name__ == '__main__':

            # Calling the function
    print(GetCountries())
