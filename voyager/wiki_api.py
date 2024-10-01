import argparse
import requests
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def search(search_term: str) -> dict:
    """
    Searches for pages on Wikivoyage using the provided search term.

    Args:
        search_term (str): The term to search for.

    Returns:
        dict: A dictionary containing the search results in JSON format.

    Note:
        The search is restricted to page titles and returns a maximum of 5 results.
    """
    api_params = {
        "action": "query",
        "list": "search",
        "format": "json",
        "formatversion": "2",
        "utf8": "1",
        "srlimit": "5",
        "srprop": "snippet",
        "srsearch": f"intitle:{search_term}",
    }

    url = "https://en.wikivoyage.org/w/api.php"
    response = requests.get(url, params=api_params)
    return response.json()


def getPage(page_id: int) -> str:
    """
    Retrieves the content of a specific page on Wikivoyage using its page ID.

    Args:
        page_id (int): The ID of the page to retrieve.

    Returns:
        str: The content of the page in plain text format.

    Raises:
        SystemExit: If the request fails with a status code other than 200.

    Note:
        This function returns the page content in plain text format and does not
        include any HTML markup.
    """
    api_params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "utf8": 1,
        "prop": "extracts",
        "rawcontinue": 1,
        "explaintext": 1,
        "pageids": page_id,
    }

    url = "https://en.wikivoyage.org/w/api.php"
    response = requests.get(url, params=api_params)

    if response.status_code == 200:
        return response.json()["query"]["pages"][0]["extract"]
    else:
        console.print(
            f"Error: Request failed with status code {response.status_code}.",
            style="red",
        )
        raise SystemExit()


def displaySearchResults(data: dict):
    """
    This function takes a dictionary as input, checks if it contains a 'query'
    key with a 'search' key inside, and then prints the 'title' and 'snippet'
    from each item in the 'search' list.

    Args:
        data (dict): Dictionary containing search results.

    Returns:
        None
    """
    print()
    if "query" in data and "search" in data["query"]:
        for index, result in enumerate(data["query"]["search"], 1):
            if "title" in result and "snippet" in result:
                console.print(
                    f"[not bold]{index}[/not bold]. {result['title']}", style="cyan"
                )
                console.print(
                    Markdown(
                        result["snippet"]
                        .replace('<span class="searchmatch">', "**")
                        .replace("</span>", "**")
                        + "..."
                    )
                )
                print()  # Empty line for separation
            else:
                print("Result missing 'title' or 'snippet' keys.")
    # TODO: Rework to handle missing results better - ideally show why
    else:
        print("Unexpected results. Exiting.")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a location")
    parser.add_argument("location", type=str, help="Location to search")
    args = parser.parse_args()

    results = search(args.location)
    page = getPage(results["query"]["search"][0]["pageid"])
    print(page)
