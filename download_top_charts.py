import os
import requests
import time

from bs4 import BeautifulSoup

from constants import (
    BASE_URL,
    LIMIT_PARAM,
    NUM_CHARTS_PAGES_TO_DOWNLOAD,
    TOP_CHARTS_PAGES_DIRECTORY,
    VERBOSE
)
from utils import top_anime_filename, prepare_to_download

if __name__ == "__main__":
    """
    This script downloads and saves the first 400 pages from the top anime charts. 
    """

    start_page = prepare_to_download(TOP_CHARTS_PAGES_DIRECTORY)
    for page in range(start_page, NUM_CHARTS_PAGES_TO_DOWNLOAD):

        # Download the page
        response = requests.get(BASE_URL, params={LIMIT_PARAM: 50*page})

        # Prettify and save it
        with open(os.path.join(TOP_CHARTS_PAGES_DIRECTORY, top_anime_filename(page), "w")) as fout:
            soup = BeautifulSoup(response.content, features="lxml")
            fout.write(soup.prettify())

        # Log progress, if running verbosely
        if VERBOSE and page%20 == 0:
            print(f"{page}/{NUM_CHARTS_PAGES_TO_DOWNLOAD} pages downloaded...")

        time.sleep(0.5)  # Let's try and avoid an IP ban
