import heapq
import os
from pathlib import Path
from scipy.spatial.distance import cosine

from constants import VOCABULARY_FILE, SECOND_INDEX_FILE, SEARCH_INFO_DIRECTORY
from utils import retrieve_title_synopsis_and_url, search_info_filename


def load_second_index():
    """
    Load the first index from the file where it was saved.
    """
    index = []

    with open(SECOND_INDEX_FILE, "r") as fin:
        for line in fin.readlines():
            tokens = line.strip().split(" ")

            index_row = []
            # Iterate over (document_id, tf-idf) pairs
            for i in range(0, len(tokens), 2):
                document_id = int(tokens[i])
                tf_idf = float(tokens[i+1])
                index_row.append((document_id, tf_idf))
            index.append(index_row)

    return index


def compute_document_vector(document_id, query, vocabulary, index):
    """Return the vector for a document, to be used in the cosine similarity check."""
    vector = [0.0]*len(query)

    for i, query_term in enumerate(query):
        for current_doc_id, tfidf in index[vocabulary.index(query_term)]:
            if document_id == current_doc_id:
                vector[i] = tfidf

    return vector


def cosine_similarity(v1: list[float], v2: list[float]):
    """Compute the cosine similarity between two vectors."""
    return 1.0 - cosine(v1, v2)


def run_query_on_second_index(query: list[str], limit: int = 10) -> list[tuple[str, str, str, float]]:
    """
    Given a query, return title, synopsis, url and query score of the first `limit` animes with the best score.
    """
    with open(VOCABULARY_FILE, "r") as fin:
        vocabulary = [word.strip() for word in fin.readlines()]

    if len(query) < 2:
        raise Exception("Please supply at least two query terms")

    if any(word.lower() not in vocabulary for word in query):  # If a word is missing from the vocabulary, the query can't be matched
        return []

    index = load_second_index()

    # We have to compute the cosine similarity between the query and all documents.
    # Let's first compute the query vector

    query_vector = [1.0]*len(query)

    # Now let's compute scores for each document and add them to a heap
    heap = []

    files_to_parse = sorted(Path(SEARCH_INFO_DIRECTORY).glob("*.txt"))
    for i, path in enumerate(files_to_parse):

        # Compute the vector for the document.
        document_vector = compute_document_vector(i, query, vocabulary, index)

        # Compute the cosine similarity
        score = cosine_similarity(query_vector, document_vector)

        if not all(vector_dimension == 0 for vector_dimension in document_vector):
            heap.append((-score, i)) # Use -score to have pop return elements from highest to lowest

    # Build list to be returned
    heapq.heapify(heap)
    result = []

    for i in range(min([limit, len(heap)])):
        score, document_id = heapq.heappop(heap)
        # Revert the sign change on score
        result.append(list(retrieve_title_synopsis_and_url(document_id)) + [-score])
    return result


if __name__ == "__main__":
    """
    Test to check that the method defined above works as expected.
    """
    for title, synopsis, url, score in run_query_on_second_index(["edward", "alphonse", "elric", "alchemy"], limit=10):
        print(title, score)