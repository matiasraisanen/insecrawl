# Insecrawl

![Python3.7](https://img.shields.io/badge/python-3.7-green)

Insecam Crawler

Downloads still frames from IP cameras listed on [insecam.org](https://www.insecam.org/)

Uses OpenCV to scrape stills off of the IP camera live streams.

**DISCLAIMER:**  
**I am in no way affiliated with insecam. I just wanted to have an easier way of browsing cameras on the site.**

## Run

Run the program simply like so:

```
$ python3 insecrawl.py -c [COUNTRYCODE]
```

---

**Example-1:** List all countries, their 2-letter code and how many cameras they each have:

```
$ python3 insecrawl.py -C
```

---

**Example-2:** Scrape all images for cameras located in Finland, and print verbose logs to stdout:

```
$ python3 insecrawl.py -c FI -v
```

---

**Example-3:** Download a still image of camera ID 241666, and append timestamp to filename

```
$ python3 insecrawl.py -o 241666 -t
```

---

You can also combine terminal commands to your liking:

**Example-4:** Scrape camera ID 241666 every 900 seconds (15 minutes).
Save images into **./images/214666_timelapse** and use timestamps in filenames. Great way to create frames for timelapse videos.

```
$ watch -n 900 "python3 insecrawl.py -o 241666 -f images/241666_timelapse -t"
```

---

Downloaded images will be saved in **./images** by default.

Camera IDs are those found on insecam.org.  
i.e. the ID of https://www.insecam.org/en/view/241666/ is **241666**

## Arguments

```
-h, --help          Print this help page

-c, --country       Designate a country, and scrape stills from all cameras in
                    that country. Provide a two letter country code (ISO 3166-1 alpha-2)

-C, --countryList   Prints all countries, country codes and camera amounts listed on
                    insecam.org

-d, --details       Prints details for a given camera ID.

-t, --timeStamp     Append timestamp to image filename. Useful if you don't
                    want to overwrite previously saved images. Timestamp
                    format is [YYYY-MM-DD]-[HH:MM:SS], using computer's
                    local time and a 24h clock.

-f, --folder        Provide a custom path for downloaded images. If not
                    provided, images will be saved to the default
                    folder ./images

-o, --oneCamera     Provide a single insecam camera ID to download a still frame from.

-u, --url           Provide a direct URL to a video stream to download a still frame
                    from. Useful if the camera is no longer on insecam, but still
                    has a publicly accessible web interface. Must be used in conjuction
                    with -i or --identifier.

-i, --identifier    Provide a custom identifier for the camera, used as
                    filename for the saved image. Works only with -u and -o flags.

-v, --verbose       Debug level logging
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
