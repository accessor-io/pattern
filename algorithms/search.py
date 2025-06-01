import requests
from googlesearch import search

def search_ethereum_json_files(query, num_results=10):
    """
    Searches for Ethereum-related JSON files using Google search.
    """
    # Google search query
    dork_query = f'intitle:"index of" {query} filetype:json'

    print(f"Searching for: {dork_query}")
    results = []
    try:
        # Retrieve search results
        for result in search(dork_query, pause=2.0):
            print(f"Found URL: {result}")
            results.append(result)
            if len(results) >= num_results:
                break
    except Exception as e:
        print(f"An error occurred during the search: {e}")

    return results

def fetch_file_contents(url):
    """
    Fetches and returns the contents of a JSON file from a URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        if "json" in response.headers.get("Content-Type", ""):
            return response.text
        else:
            print(f"URL does not contain a JSON file: {url}")
            return None
    except Exception as e:
        print(f"Failed to fetch contents from {url}: {e}")
        return None

if __name__ == "__main__":
    query = "ethereum"  # Customize this query for Ethereum-related files
    results = search_ethereum_json_files(query, num_results=10)

    for url in results:
        # Try fetching the contents of the file (if it's a direct link to a JSON file)
        print(f"\nFetching contents from: {url}")
        content = fetch_file_contents(url)
        if content:
            print(f"Preview of content from {url}:\n{content[:500]}...\n")
