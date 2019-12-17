# Insecrawl

Insecam Crawler

Crawls insecam pages on your command, and downloads a still frame from cameras.

Written in Python 3.7.

## Run

Run the program simply like so:

```
$ python3 insecrawl.py -c [COUNTRYCODE]
```

---

**Example:** Scrape all images for cameras located in Finland, and provide verbose logging:

```
$ python3 insecrawl.py -c FI -v
```

---

**Example:** Download a still image of camera ID 241666, and append timestamp to filename

```
$ python3 insecrawl.py -o 241666 -t
```

---

Downloaded images will be saved in **./images** folder.

Camera IDs are those found on insecam.org.  
i.e. isothe ID of https://www.insecam.org/en/view/241666/ is **241666**

## Arguments

```
-c, --country        Desired country as a two letter code (ISO 3166-1 alpha-2)

-v, --verbose        Debug level logging

-h, --help           Print this help page

-C, --countCameras   Prints the amount of camera pages and total cameras
                     of a given country.

-d, --details        Prints details for a given camera ID.

-t, --timeStamp      Append timestamp to image filename. Useful if you don't
                     want to overwrite previously saved images. Timestamp
                     format is [YYYY-MM-DD]-[HH:MM:SS], uses computer's
                     local time and a 24h clock.
```

## Project structure

```
.
├── help.txt            # Manual page / help text
├── images              # Downloaded images go here. Contents ignored by github.
├── insecrawl.py        # Main program
├── LICENSE             # License file
└── README.md           # This file
```

## Dependencies

```
$ pip3 install bs4 iso3166
```
