import os

from pathlib import Path

from constants import SEARCH_INFO_DIRECTORY, VOCABULARY_FILE, FIRST_INDEX_FILE
from utils import search_info_filename


if __name__ == "__main__":
    """
    This scripts builds the first inverted index described in the homework from the vocabulary and tokenized synopses.
    """

    files_to_parse = sorted(Path(SEARCH_INFO_DIRECTORY).glob("*.txt"))

    with open(VOCABULARY_FILE, "r") as fin:
        vocabulary = {word.strip(): i for i, word in enumerate(fin.readlines())}

    index = [[] for i in range(len(vocabulary))]

    for i, path in enumerate(files_to_parse):

        # Read the TXT file for this anime to extract the vocabulary's words
        with open(os.path.join(SEARCH_INFO_DIRECTORY, search_info_filename(i)), "r") as fin:
            words = set(word.strip() for word in fin.readlines()[2:])  # Skip title and URL

            for word in words:
                if word in vocabulary:  # Should always be the case, just a safety check
                    index[vocabulary[word]].append(i)  # Add the document's ID to the index

        if i % 1000 == 0:
            print(f"{i}/{len(files_to_parse)}...")

    # Save the result to a file
    with open(FIRST_INDEX_FILE, "w") as out_txt:
        for i in range(len(index)):
            # The n-th line contains the IDs of the documents that include the term with ID n
            out_txt.write(" ".join(str(doc_id) for doc_id in index[i]) + "\n")
