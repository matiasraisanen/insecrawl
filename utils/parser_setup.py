def parser_setup(parser):
    parser.add_argument("--verbose", action="store_true", help="Debug level logging")

    parser.add_argument(
        "-l",
        "--listCountries",
        action="store_true",
        default=True,
        help="List all available countries",
    )
    parser.add_argument(
        "-c",
        "--country",
        type=str,
        help="Country code of the country you want to scrape",
    )
    parser.add_argument("-d", "--details", type=str, help="Get details of a camera ID")
    parser.add_argument("-o", "--oneCamera", type=str, help="Scrape only one camera ID")
    parser.add_argument(
        "-f", "--folder", type=str, help="Folder to save images to under ./images/"
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="A direct URL to a video stream to download a still frame from. Useful if the camera is no longer on insecam, but still has a publicly accessible web interface. Must be used together with --identifier",
    )
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="A custom identifier for the camera. Works only with --url or --oneCamera",
    )
    parser.add_argument(
        "--scrapeAllCameras",
        action="store_true",
        help="Scrape all cameras on insecam. This can take hours to complete.",
    )
    parser.add_argument(
        "--sortByCountry",
        action="store_true",
        default=True,
        help="Images will be saved in ./images/{COUNTRY_NAME}",
    )
    parser.add_argument(
        "--sortByCamera",
        action="store_true",
        help="Images will be saved in ./images/{CAMERA_ID}",
    )
    parser.add_argument(
        "--newCamsOnly",
        action="store_true",
        help="Only scrape cameras that have not been scraped before (determined by filename on disk)",
    )
    parser.add_argument(
        "--timeStamp",
        action="store_true",
        help="Add a timestamp to the filename of the image",
    )
    parser.add_argument(
        "--interval",
        type=int,
        help="Provide an amount of seconds you wish to wait between each run. Works only in  conjuction with -c or --country. The interval starts to run after the last camera is scraped, so don't expect exact results with  this. Can be exited only with CTRL+C.",
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")
