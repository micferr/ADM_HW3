import math
import os

from pathlib import Path

from constants import SEARCH_INFO_DIRECTORY, VOCABULARY_FILE, SECOND_INDEX_FILE
from first_index_utils import load_first_index
from utils import search_info_filename

def tf(words) -> float:
    """Boolean term frequency, weighted over the document's word count."""

    return 1/len(words)

def idf(num_all_documents, num_documents_containing_term) -> float:
    """Inverse document frequency for a word. Uses the precomputed data from the first index."""

    return math.log(num_all_documents/num_documents_containing_term)

if __name__ == "__main__":
    """
    This scripts builds the second inverted index described in the homework from the vocabulary and tokenized synopses.
    """

    files_to_parse = sorted(Path(SEARCH_INFO_DIRECTORY).glob("*.txt"))
    num_all_documents = len(files_to_parse)

    with open(VOCABULARY_FILE, "r") as fin:
        vocabulary = {word.strip(): i for i, word in enumerate(fin.readlines())}

    first_index = load_first_index()  # Used to compute inverse document frequencies

    index = [[] for i in range(len(vocabulary))]

    for i, path in enumerate(files_to_parse):

        # Read the TXT file for this anime to extract the vocabulary's words
        with open(os.path.join(SEARCH_INFO_DIRECTORY, search_info_filename(i)), "r") as fin:
            words = set(word.strip() for word in fin.readlines()[2:])  # Skip title and URL

            for word in words:
                if word in vocabulary:  # Should always be the case, just a safety check
                    # Add the document's ID and its score to the index
                    index[vocabulary[word]].append(i)

                    _tf = tf(words)
                    num_documents_containing_term = len(first_index[vocabulary[word]])
                    _idf = idf(num_all_documents, num_documents_containing_term)
                    index[vocabulary[word]].append(_tf * _idf)

        if i % 1000 == 0:
            print(f"{i}/{len(files_to_parse)}...")

    # Save the result to a file
    with open(SECOND_INDEX_FILE, "w") as out_txt:
        for i in range(len(index)):
            # The n-th line contains the IDs of the documents that include the term with ID n followed by their tf-idf score
            out_txt.write(" ".join(str(value) for value in index[i]) + "\n")
