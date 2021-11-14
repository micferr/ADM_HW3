from constants import VOCABULARY_FILE, FIRST_INDEX_FILE
from utils import retrieve_title_synopsis_and_url


def load_first_index():
    """
    Load the first index from the file where it was saved.
    """
    index = []

    with open(FIRST_INDEX_FILE, "r") as fin:
        for documents_ids_line in fin.readlines():
            documents_ids = [int(_id) for _id in documents_ids_line.split(" ")]
            index.append(documents_ids)

    return index


def run_query_on_first_index(query: list[str]) -> list[tuple[str, str, str]]:
    """
    Given a query, return title, synopsis and url of the animes that match it.
    """
    with open(VOCABULARY_FILE, "r") as fin:
        vocabulary = [word.strip() for word in fin.readlines()]

    if not query:
        raise Exception("Please supply at least one query term")

    if any(word.lower() not in vocabulary for word in query):  # If a word is missing from the vocabulary, the query can't be matched
        return []

    index = load_first_index()

    # First retrieve all documents matching the first query term
    matches = set(index[vocabulary.index(query[0])])

    # Then compute the intersection with all other terms' partial matches
    for query_term in query[1:]:
        partial_result = set(index[vocabulary.index(query_term)])
        matches = matches.intersection(partial_result)

    return [retrieve_title_synopsis_and_url(i) for i in matches]


if __name__ == "__main__":
    """
    Test to check that the method defined above works as expected.
    """
    print(run_query_on_first_index(["saiyan"]))