import csv
import os
from datetime import datetime
from pathlib import Path

from constants import TOP_CHARTS_PAGE_NAME, ANIME_PAGE_NAME, PARSED_ANIME_PAGE_NAME, SEARCH_INFO_FILE_NAME, \
    PARSED_ANIMES_DIRECTORY, TOP_ANIME_URLS_FILE


def top_anime_filename(page):
    """
    Return the filename for the file in which the page-th (0-indexed) top chart page is saved.
    """
    return TOP_CHARTS_PAGE_NAME.format(f"{page:03}")  # Page can be up to 399


def anime_filename(index):
    """
    Return the filename for the file in which an individual anime's page is saved.

    Animes are indexed by their position in the top chart, starting at 0.
    """
    return ANIME_PAGE_NAME.format(f"{index:05}")  # Page can be up to 19129


def parsed_anime_filename(index):
    """
    Return the filename for the file in which an individual anime's parsed info is saved.
    """
    return PARSED_ANIME_PAGE_NAME.format(f"{index:05}")


def search_info_filename(index):
    """
    Return the filename for the file in which an individual anime's search info is saved.
    """
    return SEARCH_INFO_FILE_NAME.format(f"{index:05}")


def prepare_to_download(directory: str) -> int:
    """
    Prepare the environment to start downloading pages.

    The method ensures the folder in which to store the pages exists and returns the page by which to start downloading
    (starting at 0).
    """
    directory = Path(directory)
    directory.mkdir(exist_ok=True)
    return len(list(directory.glob("*.html")))


def retrieve_title_synopsis_and_url(i: int) -> tuple[str, str, str]:
    """
    Return the title, unprocessed synopsis and url of the i-th anime.
    """
    with open(TOP_ANIME_URLS_FILE, "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]

    with open(os.path.join(PARSED_ANIMES_DIRECTORY, parsed_anime_filename(i)), "r") as fin:
        csv_reader = csv.reader(fin, delimiter="\t")
        next(csv_reader)  # Skip headers
        data = next(csv_reader)

        return data[0], data[10], urls[i]


class Anime:
    """
    Class to represent the information parsed from an anime page.
    """

    animeTitle: str
    animeType: str
    animeNumEpisode: str
    releaseDate: datetime
    endDate: datetime
    animeNumMembers: int
    animeScore: float
    animeUsers: int
    animeRank: int
    animePopularity: int
    animeDescription: str
    animeRelated: list[str]
    animeCharacters: list[str]
    animeVoices: list[str]
    animeStaff: list[list[str]]


