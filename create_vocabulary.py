import os

from pathlib import Path

from constants import SEARCH_INFO_DIRECTORY, VOCABULARY_FILE
from utils import search_info_filename


if __name__ == "__main__":
    """
    This scripts iterates the anime's search info files to extract the vocabulary and save it to a file.
    """

    files_to_parse = sorted(Path(SEARCH_INFO_DIRECTORY).glob("*.txt"))

    vocabulary = set()

    for i, path in enumerate(files_to_parse):

        # Read the TXT file for this anime to extract the vocabulary's words
        with open(os.path.join(SEARCH_INFO_DIRECTORY, search_info_filename(i)), "r") as fin:
            words = set(word.strip() for word in fin.readlines()[2:])  # Skip title and URL

            vocabulary |= words  # Update the vocabulary with the current file's words

            if i % 1000 == 0:
                print(f"{i}/{len(files_to_parse)}...")

    # Save the result to a file
    with open(VOCABULARY_FILE, "w") as out_txt:
        out_txt.write("\n".join(vocabulary))

    print(f"The vocabulary contains {len(vocabulary)} words.")
