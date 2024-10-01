import os
import json
import datetime

import google.generativeai as genai

from rich.console import Console
from rich.markdown import Markdown

console = Console()


def apiKey() -> str:
    """
    Retrieves the Gemini API key from a local config file. If the file doesn't
    exist or the API key is invalid, it prompts the user to enter a new API key
    and saves it to the config file.

    Returns:
        str: The Gemini API key.
    """
    # TODO: Branch out into separate config file and give model option
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(parent_dir, "config.json")

    if not os.path.exists(config_path):
        console.print("Gemini API key not found. Please enter your key.")
        console.print(
            "To get a new key visit: https://makersuite.google.com/app/apikey"
        )
        api_key = input()
        with open(config_path, "w") as config_file:
            config_file.write(f'{"gemini_api_key": "{api_key}"}')
    else:
        try:
            with open(config_path, "r") as config_file:
                api_key = (json.load(config_file))["gemini_api_key"]
        except:
            console.print("API key error! Deleting saved details.")
            os.remove(config_path)
            api_key = apiKey()
    return api_key


def chatWithDocumentCached(model, document, ttl_minutes: int = 5):
    """
    Creates a cached version of the given model with the given document and
    starts a new chat session.

    Args:
        model: The GenerativeModel instance to use.
        document: The document to use for the chat session.
        ttl_minutes: The time to live (in minutes) for the cached content.
        Defaults to 5.

    Returns:
        tuple: A tuple containing the chat session and the cached content.
    """
    cache = genai.caching.CachedContent.create(
        model=model.model_name,
        contents=[document],
        ttl=datetime.timedelta(minutes=ttl_minutes),
    )
    cached_model = genai.GenerativeModel.from_cached_content(cached_content=cache)
    chat = cached_model.start_chat(history=[])
    return chat, cache


def chatWithDocumentUncached(model):
    """
    Starts a new chat session with the given model without caching.

    Args:
        model: The GenerativeModel instance to use.

    Returns:
        tuple: A tuple containing the chat session and None(since there is no
        cached content).
    """
    chat = model.start_chat(history=[])
    return chat, None


def chatLoop(chat, document=None):
    """
    Runs the chat loop, prompting the user for input and displaying the response
    from the chat session.

    Args:
        chat: The chat session to use.
        document: The document to use for the chat session (optional).

    Returns:
        None
    """
    print("Chat initialized. Type 'quit' to exit.")
    while True:
        console.print("\nUser: ", style="bold cyan", end="")
        user_input = input()
        if user_input.lower() == "quit":
            console.print("\nExiting application. Goodbye!", style="bold red")
            break

        if document:
            response = chat.send_message([user_input, document])
        else:
            response = chat.send_message(user_input)
        console.print("Assistant: ", style="bold magenta", end="")
        console.print(Markdown(f"{response.text}"))
        # print(f"Token usage: {response.usage_metadata}\n")


def pageChat(content: str):
    """
    Runs the chat loop for a given page content, using a cached version of the
    contents if it's too large.

    Args:
        content: The page content to use for the chat session.

    Returns:
        None
    """
    if len(content) < 10:
        console.print("Error! Page contents missing. Exiting.", style="bold red")
        return

    # setup model
    api_key = apiKey()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash-001",
        system_instruction=(
            "You are an expert travel guide. Your job is to answer the user's"
            "query based on the document you have access to. Try giving them"
            "suggestions and answers that would help them decide their next"
            "travel destination."
        ),
    )

    # chat with doc
    token_count = model.count_tokens(content).total_tokens
    if token_count > 40000:
        print("Large page encountered, caching page.")
        chat, cache = chatWithDocumentCached(model, content)
        chatLoop(chat)
    else:
        chat, cache = chatWithDocumentUncached(model)
        chatLoop(chat, content)

    # if cache was created, get rid of it.
    if cache:
        cache.delete()
