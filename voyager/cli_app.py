from voyager import wiki_api, llm_chat

import argparse
from rich.console import Console
from pyfiglet import figlet_format

console = Console()


def entryPoint(search_term: str) -> None:
    """
    Queries the Wikivoyage API for a search term and initiates a conversation
    with the user about the chosen result.

    Args:
        search_term (str): The term to search for in the Wikipedia API.

    Returns:
        None
    """
    # search for location and display options
    results = wiki_api.search(search_term)
    wiki_api.displaySearchResults(results)

    # input page option and initiate chat
    # TODO: handle bad input
    option = int(input("Enter choice: "))
    page = wiki_api.getPage(results["query"]["search"][option - 1]["pageid"])
    llm_chat.pageChat(page)


def main() -> None:
    """
    The main entry point of the Voyager application.

    Initializes the application by displaying a title graphic and prompting the
    user to enter a search location.

    Returns:
        None
    """
    # Title graphic
    console.print(figlet_format("Voyager", font="larry3d"), style="bold cyan")

    # search for location and enter app
    console.print("Enter a location to search: ", style="cyan", end="")
    search_location = input()
    entryPoint(search_location)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search for a location")
    parser.add_argument("location", type=str, help="Location to search")
    args = parser.parse_args()
    entryPoint(args.location)
