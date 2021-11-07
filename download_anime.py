import os
import time

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from constants import TOP_ANIME_URLS_FILE, ANIMES_DIRECTORY, VERBOSE
from utils import prepare_to_download, anime_filename

if __name__ == "__main__":
    """
    This script downloads all the pages in the "top_anime_urls.txt" file and saves them.
    
    If for whatever reason the script is stopped, it can be relaunched as is and will continue from where it left off.
    
    In case the rate limit is exceeded, the script wait a bit before trying again. 
    In a production environment either a proper framework (e.g. Scrapy) or, even better, the platform's API should be
    used to retrieve a platform's data.
    """
    with open(TOP_ANIME_URLS_FILE, "r") as fin:
        urls = fin.readlines()

    start_page = prepare_to_download(ANIMES_DIRECTORY)

    for index, url in enumerate(urls[start_page:], start_page):

        download_ok = False
        backoff = 10  # Time to wait after an error before retrying

        # Attempt downloading the page until success, with an incremental backoff in case of errors.
        #
        # This is a simple implementation since we have to implement everything from scratch, otherwise a library
        # like [Tenacity](https://github.com/jd/tenacity) could be used.
        while not download_ok:
            # Download the page
            try:
                response = requests.get(url.strip())
                response.raise_for_status()  # Raise if the request was not successful
                download_ok = True
            except HTTPError as err:
                print(f"Error downloading file #{index}, let's wait {backoff} seconds...")
                time.sleep(10)
                backoff += 10  # Use an incremental backoff

        # Prettify and save it
        with open(os.path.join(ANIMES_DIRECTORY, anime_filename(index)), "w") as fout:
            soup = BeautifulSoup(response.content, features="lxml")
            fout.write(soup.prettify())

        if VERBOSE and index%100 == 0:
            print(f"{index}/{len(urls)} pages downloaded")
