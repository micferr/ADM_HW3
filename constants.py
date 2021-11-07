"""This file contains all the common constants."""

BASE_URL = "https://myanimelist.net/topanime.php"  # The base URL to MyAnimeList's Top Anime list page
LIMIT_PARAM="limit"  # The name of the limit parameter to query the page

NUM_ANIMES_PER_PAGE = 50  # How many animes appear in each Top Anime page
NUM_CHARTS_PAGES_TO_DOWNLOAD = 400  # How many pages from the Top Anime list to download
TOP_CHARTS_PAGE_NAME = "top_animes_page_{}.html"  # Filename with which to store pages
TOP_CHARTS_PAGES_DIRECTORY = "top_chart"  # Name of the directory in which to store the fetched Top Anime webpages

TOP_ANIME_URLS_FILE = "top_anime_urls.txt"  # The file in which to store the URLs of all animes

ANIMES_DIRECTORY = "animes"  # The directory in which to store the fetched individual animes' pages
ANIME_PAGE_NAME = "anime_{}.html"  # The base name of the individual animes' pages.

VERBOSE = True  # Whether to log progress
