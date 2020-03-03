# Insecrawl

![Python3.7](https://img.shields.io/badge/python-3.7-green)

Insecrawl is a crawler for [insecam.org](https://www.insecam.org/). Its purpose is to download still frames from cameras listed on said website.

The script can scrape an image from a single camera, all cameras in a certain country, or just simply every camera found on the site.

The script is automated, so the user can just issue a command, go make a sandwich, and come back to a folder full of stills from interesting cameras.

Downloaded images will be saved in **./images** by default.

Camera IDs are those listed on insecam.org.  
i.e. the ID of https://www.insecam.org/en/view/241666/ is **241666**

**DISCLAIMER:**  
**I am in no way affiliated with insecam. I just wanted to have an easier way of browsing cameras on the site.**

---

## How to use

There are several ways to use this program, but the suggested use is as follows:

**1. List cameras by country**

```
$ python3 insecrawl.py -l
```

**2. Pick a country code from the list, and scrape its cameras**

```
$ python3 insecrawl.py -t -S -c FI
```

| Flag  | Explanation                                                                                                |
| :---- | :--------------------------------------------------------------------------------------------------------- |
| -t    | Add a timestamp to the image filename. Prevents overwriting previous scrapes.                              |
| -S    | Automatically determine the filepath using the country code. e.g. FI will be saved in **./images/Finland** |
| -c FI | Scrape cameras from FI                                                                                     |

**3. Browse ./images/Finland to see the scraped images**

---

## Examples

**Example-1:**  
List all countries, their two-letter code and how many cameras they each have

```
$ python3 insecrawl.py --listCountries
```

---

**Example-2:**  
Scrape images from every camera listed on insecam, and save them in **./images/{COUNTRY_NAME}**  
This can take a couple of hours to finish.

```
$ python3 insecrawl.py --scrapeAllCameras --sortByCountry
```

---

**Example-3:**  
You can also combine terminal commands to your liking.

Scrape camera ID 241666 every 900 seconds.
Save images into **./images/214666_timelapse** and use timestamps in filenames. Great way to create frames for timelapse videos.

```
$ watch -n 900 "python3 insecrawl.py -o 241666 -f 241666_timelapse -t"
```

---

## Options

```
-h, --help          Print this help page

-c, --country       Designate a country, and scrape stills from all cameras in
                    that country. Provide a two letter country code (ISO 3166-1 alpha-2)

-l, --listCountries Prints all countries, country codes and camera amounts listed on
                    insecam.org

-d, --details       Prints details for a given camera ID.

-f, --folder        Assign a custom download path under ./images folder.

-i, --identifier    Provide a custom identifier for the camera, used as
                    filename for the saved image. Works only with -u and -o flags.

-n, --newCamsOnly   Scrape only the cameras that do not have a still saved on disk.

-o, --oneCamera     Provide a single insecam camera ID to download a still frame from.

--scrapeAllCameras  Downloads a still from every camera listed on insecam. This can
                    take hours to complete. Best used together with --sortByCountry

-S, --sortByCountry Images will be saved in ./images/{COUNTRY_NAME}

-t, --timeStamp     Append timestamp to image filename. Useful if you don't
                    want to overwrite previously saved images. Timestamp
                    format is [YYYY-MM-DD]-[HH:MM:SS], using computer's
                    local time and a 24h clock.

-u, --url           Provide a direct URL to a video stream to download a still frame
                    from. Useful if the camera is no longer on insecam, but still
                    has a publicly accessible web interface. Must be used in conjuction
                    with -i or --identifier.

-v, --verbose       Debug level logging
```

---

## 3rd party dependencies

- [opencv-python](https://pypi.org/project/opencv-python/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [iso3166](https://pypi.org/project/iso3166/)
