import csv
import os
from datetime import datetime
from typing import Tuple, Optional

import bs4
import re
from bs4 import BeautifulSoup
from pathlib import Path

from constants import ANIMES_DIRECTORY, PARSED_ANIMES_DIRECTORY
from utils import Anime, prepare_to_download, parsed_anime_filename


def get_tag_text(tag: Optional[bs4.element.Tag]) -> Optional[str]:
    """Utility to retrieve and strip the text of a tag, defaulting to None if missing."""
    return ''.join(tag.find_all(text=True, recursive=False)).strip() if tag else None


def extract_title(soup: BeautifulSoup) -> str:
    """Extract an anime's title."""
    return soup.find("div", class_="h1-title").div.h1.strong.get_text().strip()


def _parse_airing_dates(dates: Optional[str]) -> Tuple[Optional[datetime], Optional[datetime]]:
    """Parse and return the airing date(s) of the anime."""

    def to_datetime(d: str):
        if not any(char.isdigit() for char in d): # To account for missing data (Unknown, Not Available, ?)
            return None

        return datetime.strptime(d, "%b %d, %Y")

    if re.search(" to ", dates):
        date1, date2 = tuple(dates.split(" to "))
        return to_datetime(date1), to_datetime(date2)

    if re.search(" - ", dates):
        date1, date2 = tuple(dates.split(" - "))
        return to_datetime(date1), to_datetime(date2)

    if re.match("[A-Za-z]+ [0-9]+, [0-9]+", dates): # Only one date
        date = to_datetime(dates)
        return date, date


def extract_type_episodes_and_dates(soup: BeautifulSoup) -> Tuple[str, int, Optional[datetime], Optional[datetime]]:
    """Extract an anime's type, number of episodes and start/end dates."""

    type_tag = soup.find("span", text=lambda text: text and "Type:" in text)
    if type_tag:
        _type = get_tag_text(type_tag.parent)
    else:
        _type = None

    episodes_tag = soup.find("span", text=lambda text: text and "Episodes:" in text)
    episodes = None
    if episodes_tag:
        try:
            episodes = int(get_tag_text(episodes_tag.parent))
        except:
            pass

    dates_tag = soup.find("span", text=lambda text: text and "Aired:" in text)
    start_date, end_date = None, None
    if dates_tag:
        try:
            start_date, end_date = _parse_airing_dates(get_tag_text(dates_tag.parent))
        except:
            pass

    return _type, episodes, start_date, end_date


def extract_score_info(soup: BeautifulSoup, rank: int) -> Tuple[int, float, int, int, int]:
    """Extract an anime's members, score, users, rank and popularity."""
    members, score, users, popularity = 0, 0.0, 0, 0

    try:
        members_text = get_tag_text(soup.find("span", class_="numbers members"))
        if members_text:
            members = int(members_text.replace(",", ""))
    except:
        members = None

    try:
        score = int(get_tag_text(soup.find("span", {"itemprop": "ratingValue"})))
    except:
        score = None

    try:
        users = int(get_tag_text(soup.find("span", {"itemprop", "ratingCount"})))
    except:
        users = None

    try:
        popularity_text = get_tag_text(soup.find("span", class_="numbers popularity"))
        if popularity_text:
            popularity = int(popularity_text.replace(",", ""))
    except:
        popularity = None

    return members, score, users, rank, popularity


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """Extract an anime's synopsis."""
    tag = soup.find("p", {"itemprop": "description"})
    return get_tag_text(tag) if tag else None


def extract_related_anime(soup: BeautifulSoup) -> list[str]:
    """Extract an anime's list of related animes."""
    related_anime_table = soup.find("table", class_="anime_detail_related_anime")
    if not related_anime_table:
        return []

    related_anime_names = set()

    # Related animes must have a link (and the link must start with /anime, otherwise it's a manga)
    for anime_link in related_anime_table.find_all("a", href=lambda href: re.match("/anime", href)):
        anime_name = get_tag_text(anime_link)
        related_anime_names.add(anime_name)

    return list(related_anime_names)


def extract_characters_and_voices(soup: BeautifulSoup) -> tuple[list[str], list[str]]:
    """Extract an anime's characters and their voice actors."""
    characters_div = soup.find("div", class_="detail-characters-list") # First one is characters/VAs, second is staff
    if not characters_div:
        return [], []

    characters = [get_tag_text(tag.a) for tag in characters_div.find_all("h3", class_="h3_characters_voice_actors") or []]
    voices = [
        get_tag_text(tag)
        for tag
        in characters_div.find_all("a", href=lambda href: re.search("/people/", href) is not None, text=lambda text: text) or []
    ]

    return characters, voices


def extract_anime_staff(soup: BeautifulSoup) -> list[list[str]]:
    """Extract an anime's staff."""
    divs = list(soup.find_all("div", class_="detail-characters-list"))
    if len(divs) < 2:
        return []

    staff_div = divs[1]
    staff = []
    for a_tag in staff_div.find_all("a"):
        if a_tag.img: # Skip images
            continue

        try:
            role_tag = a_tag.parent.div.small
            staff.append([get_tag_text(a_tag), get_tag_text(role_tag)])
        except:
            pass

    return staff


if __name__ == "__main__":
    """
    This scripts iterates the individual anime's pages. For each anime, it parses the required information
    and saves them to a TSV file.
    """
    files_to_parse = sorted(Path(ANIMES_DIRECTORY).glob("*.html"))
    start_file = prepare_to_download(PARSED_ANIMES_DIRECTORY)

    try:
        for i, path in enumerate(files_to_parse[start_file:], start=start_file):

            with open(path, "r") as fin:
                soup = BeautifulSoup(fin, "html.parser")
                anime = Anime()

                anime.animeTtle = extract_title(soup)
                anime.animeType, anime.animeNumEpisode, anime.releaseDate, anime.endDate = extract_type_episodes_and_dates(soup)
                (
                    anime.animeNumMembers,
                    anime.animeScore,
                    anime.animeUsers,
                    anime.animeRank,
                    anime.animePopularity
                ) = extract_score_info(soup, i+1)
                anime.animeDescription = extract_description(soup)
                anime.animeRelated = extract_related_anime(soup)
                anime.animeCharacters, anime.animeVoices = extract_characters_and_voices(soup)
                anime.animeStaff = extract_anime_staff(soup)

            # Write the TSV file for this anime
            with open(os.path.join(PARSED_ANIMES_DIRECTORY, parsed_anime_filename(i)), "w") as tsv_file:
                tsv_writer = csv.writer(tsv_file, delimiter='\t')
                tsv_writer.writerow([
                    "animeTitle", "animeType", "animeNumEpisode", "releaseDate", "endDate",
                    "animeNumMembers", "animeScore", "animeUsers", "animeRank", "animePopularity",
                    "animeDescription", "animeRelated", "animeCharacters", "animeVoices", "animeStaff"
                ])
                tsv_writer.writerow([
                    anime.animeTtle, anime.animeType, anime.animeNumEpisode, anime.releaseDate, anime.endDate,
                    anime.animeNumMembers, anime.animeScore, anime.animeUsers, anime.animeRank, anime.animePopularity,
                    anime.animeDescription, anime.animeRelated, anime.animeCharacters, anime.animeVoices, anime.animeStaff
                ])

            if i%100 == 0:
                print(f"{i}/{len(files_to_parse)}...")
    except Exception as e:
        print(str(path))  # Log which file caused the error
        raise e
