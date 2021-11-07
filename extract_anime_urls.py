import os

from bs4 import BeautifulSoup

from constants import NUM_CHARTS_PAGES_TO_DOWNLOAD, TOP_CHARTS_PAGES_DIRECTORY, TOP_ANIME_URLS_FILE, VERBOSE, \
    NUM_ANIMES_PER_PAGE
from utils import top_anime_filename


if __name__ == "__main__":
    """
    This script iterates the pages retrieved by the `download_top_anime.py` script to extract
    the 400*50 animes' URLs in a TXT file.
    """

    urls = []
    for page in range(NUM_CHARTS_PAGES_TO_DOWNLOAD):
        with open(os.path.join(TOP_CHARTS_PAGES_DIRECTORY, top_anime_filename(page)), "r") as fin:

            soup = BeautifulSoup(fin, "lxml")

            # Links are in the A tag in the second TD of each TR with class "ranking-list"
            animes_in_page = list(soup.find_all("tr", class_="ranking-list"))

            for anime in animes_in_page:
                url = anime.find_all("td")[1].a.get("href")
                urls.append(url + "\n")

            # This gets triggered, so there are less than (400*50 = 20'000) animes!
            if len(animes_in_page) != NUM_ANIMES_PER_PAGE:
                print(f"{top_anime_filename(page)} only has {len(animes_in_page)} animes.")

        if VERBOSE and page%20 == 0:
            print(f"{page}/{NUM_CHARTS_PAGES_TO_DOWNLOAD} pages parsed")

    with open(TOP_ANIME_URLS_FILE, "w") as fout:
        fout.writelines(urls)

    # We noticed there are less than 20k animes. Let's count how many there are.
    print(f"{len(urls)} anime URLs parsed")  # Prints "19130 anime URLs parsed"