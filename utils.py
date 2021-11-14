from datetime import datetime
from pathlib import Path

from constants import TOP_CHARTS_PAGE_NAME, ANIME_PAGE_NAME, PARSED_ANIME_PAGE_NAME


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
    Return the filename for the file in which an individual anime's page is saved.

    Animes are indexed by their position in the top chart, starting at 0.
    """
    return PARSED_ANIME_PAGE_NAME.format(f"{index:05}")  # Page can be up to 19129


def prepare_to_download(directory: str) -> int:
    """
    Prepare the environment to start downloading pages.

    The method ensures the folder in which to store the pages exists and returns the page by which to start downloading
    (starting at 0).
    """
    directory = Path(directory)
    directory.mkdir(exist_ok=True)
    return len(list(directory.glob("*.html")))


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


