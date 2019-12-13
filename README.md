# Insecrawl

Insecam Crawler

Crawls insecam pages on your command, and downloads a still frame from cameras.

Written in Python 3.7.

## Run

Run the program simply like so:

```
$ python3 insecrawl.py -c [COUNTRYCODE]
```

**Example:** Scrape all images for cameras located in Finland, and provide verbose logging:

```
$ python3 insecrawl.py -c FI -v
```

Downloaded images will be saved in **./images** folder.

Possible arguments:

```
-c, --country        Desired country as a two letter code (ISO 3166-1 alpha-2)
-v, --verbose        Debug level logging
-h, --help           Print this help page
-P, --pageCount      Prints the amount of camera pages of a given country
-p, --pages          Scrape this many pages.
```

## Project structure

```
.
├── images              # Downloaded images go here. Contents ignored by github.
│   └── .gitignore
├── insecrawl.py        # Main program
├── LICENSE             # License file
└── README.md           # This file
```

## Dependencies

```
$ pip3 install bs4 iso3166
```
