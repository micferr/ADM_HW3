import csv
import heapq
import os
from pathlib import Path
from scipy.spatial.distance import cosine

from constants import VOCABULARY_FILE, SECOND_INDEX_FILE, SEARCH_INFO_DIRECTORY, PARSED_ANIMES_DIRECTORY
from second_index_utils import load_second_index, cosine_similarity
from utils import retrieve_title_synopsis_and_url, search_info_filename, parsed_anime_filename


def compute_document_vector(document_id, query, vocabulary, index, requested_popularity, popularity, popularity_range):
    """Return the vector for a document, to be used in the cosine similarity check."""
    vector = [0.0]*len(query)

    for i, query_term in enumerate(query):
        for current_doc_id, tfidf in index[vocabulary.index(query_term)]:
            if document_id == current_doc_id:
                vector[i] = tfidf

    # Custom metric: match requested popularity
    weighted_popularity = (popularity - popularity_range[0])/(popularity_range[1] - popularity_range[0])
    if requested_popularity == "popular":
        vector += [weighted_popularity] # 1 to the most popular, 0 to the least popular, the others in between
    elif requested_popularity == "unpopular":
        vector += [1.0-weighted_popularity] # Opposite to the above

    return vector


def run_custom_query(query: list[str], requested_popularity: str, limit: int = 10) -> list[tuple[str, str, str, float]]:
    """
    Given a query, return title, synopsis, url and query score of the first `limit` animes with the best score.
    """
    with open(VOCABULARY_FILE, "r") as fin:
        vocabulary = [word.strip() for word in fin.readlines()]

    if len(query) < 1:
        raise Exception("Please supply at least one query term")

    if requested_popularity not in ("popular", "unpopular"):
        raise Exception("Please supply a valid value for popularity")

    if any(word.lower() not in vocabulary for word in query):  # If a word is missing from the vocabulary, the query can't be matched
        return []

    index = load_second_index()

    # Retrieve all animes' popularity, defined as its ranking
    popularities = []

    for i, path in enumerate(sorted(Path(PARSED_ANIMES_DIRECTORY).glob("*.tsv"))):
        # Read the TSV file for this anime to extract search info
        with open(os.path.join(PARSED_ANIMES_DIRECTORY, parsed_anime_filename(i)), "r") as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter='\t')
            next(tsv_reader) # Skip headers
            data = next(tsv_reader)
            popularity = int(data[8]) if data[8] else 10000 # ranking, if missing use average (over ~19k documents)
            popularities.append(popularity)

    popularity_range = (min(popularities), max(popularities))

    # We have to compute the cosine similarity between the query and all documents.
    # Let's first compute the query vector

    query_vector = [1.0]*(len(query)+1) # Add 1 fot the new metric

    # Now let's compute scores for each document and add them to a heap
    heap = []

    files_to_parse = sorted(Path(SEARCH_INFO_DIRECTORY).glob("*.txt"))
    for i, path in enumerate(files_to_parse):

        # Compute the vector for the document.
        document_vector = compute_document_vector(i, query, vocabulary, index, requested_popularity, popularities[i], popularity_range)

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
    for title, synopsis, url, score in run_custom_query(["alchemy"], "popular", limit=10):
        print(title, score)
    for title, synopsis, url, score in run_custom_query(["alchemy"], "unpopular", limit=10):
        print(title, score)