import csv
import string
import os

import nltk

from nltk.corpus import stopwords, wordnet
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from pathlib import Path

from constants import PARSED_ANIMES_DIRECTORY, SEARCH_INFO_DIRECTORY, TOP_ANIME_URLS_FILE
from utils import prepare_to_download, parsed_anime_filename, search_info_filename


lemmatizer = WordNetLemmatizer()


def get_wordnet_pos(treebank_tag):
    """
    Convert pos_tag's tags to ones accepted by WordNetLemmatizer.

    (Adapted from https://stackoverflow.com/questions/61982023/using-wordnetlemmatizer-lemmatize-with-pos-tags-throws-keyerror)
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV

    return wordnet.NOUN  # default

def lemmatize(synopsis: str) -> set[str]:
    """Lemmatize a text returning a list of its lemmas and removing stopwords and punctuation."""
    stop_words = set(stopwords.words('english'))
    punctuation = set(char for char in string.punctuation)

    words_to_remove = stop_words | punctuation

    # Run Part-of-Speech tagging to improve tokenization
    words_and_poses = [
        word_and_pos
        for word_and_pos
        in pos_tag(word_tokenize(synopsis.lower()))
        if word_and_pos[0] not in words_to_remove
    ]

    return set(lemmatizer.lemmatize(word, get_wordnet_pos(pos)) for word, pos in words_and_poses)


if __name__ == "__main__":
    """
    This scripts iterates the parsed anime's TSV file to extract only those information required for the search engines.
    
    The synopsis is stored after NLTK processing. 
    """
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

    files_to_parse = sorted(Path(PARSED_ANIMES_DIRECTORY).glob("*.tsv"))
    start_file = prepare_to_download(SEARCH_INFO_DIRECTORY)

    with open(TOP_ANIME_URLS_FILE, "r") as url_file:
        urls = [url.strip() for url in url_file.readlines()]

    for i, path in enumerate(files_to_parse[start_file:], start=start_file):

        # Read the TSV file for this anime to extract search info
        with open(os.path.join(PARSED_ANIMES_DIRECTORY, parsed_anime_filename(i)), "r") as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter='\t')
            next(tsv_reader) # Skip headers
            data = next(tsv_reader)

            title = data[0]
            # lemmatize to get more accurate results w.r.t. stemming
            synopsis = lemmatize(data[10]) if data else []
            url = urls[i]

        with open(os.path.join(SEARCH_INFO_DIRECTORY, search_info_filename(i)), "w") as out_tsv:
            tsv_writer = csv.writer(out_tsv, delimiter='\t')
            tsv_writer.writerow(["animeTitle", "animeDescription", "Url"])
            tsv_writer.writerow([title, synopsis, url])

        if i%100 == 0:
            print(f"{i}/{len(files_to_parse)}...")
