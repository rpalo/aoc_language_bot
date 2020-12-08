import argparse
from collections import Counter
from itertools import chain
import json
import logging
import sys
from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


def get_article_ids(urls, history):
    """Given a list of regular copy/pasted web URLs to posts,
    pings the API to get the article_id of each for the comment queries.
    Uses the cache if possible.

    NOTE: the order of the URLs in the file is important, as it drives
    which article is specified for which Day of the challenge.
    """ 
    for day, url in enumerate(urls, start=1):
        if url in history:
            logging.info(f"Using day {day} from cache.")
            continue

        time.sleep(1)  # Be a good citizen
        protocol, domain, user_slug = url.partition("dev.to/")
        api_url = protocol + domain + "api/articles/" + user_slug
        result = requests.get(api_url)

        if result.status_code != 200:
            logging.error(f"Couldn't get {api_url}.")
            continue
        data = result.json()
        logging.info(f"Retreived day {day} from the API.")
        history[url] = {
            "id": data["id"],
            "title": data["title"],
            "day": day,
            "comments": dict(),
        }


def get_user_decision(soup, code_block):
    """Gets user input on a comment it's not able to classify.
    
    Separate multiple languages in a single post with a '/'.
    """
    print("Need input.", soup.prettify(), sep="\n")
    while True:
        language = input("Language (<Enter> for None): ") or "None"
        confirm = input(f"Confirm you meant '{language}' (y/n): ")
        if confirm in ['y', 'Y']:
            return [lang.capitalize() for lang in language.split('/')]


def parse_comment(comment):
    """Parses a comment's HTML looking for a highlighted `pre` tag.
    
    `comment` is a dict from DEV's comment API.
    """
    soup = BeautifulSoup(comment["body_html"], "html.parser")
    code_block = soup.find("pre", class_="highlight")

    # TODO: Check to see if the comment contains any language names from a list

    if code_block != None and code_block["class"][-1] != "plaintext":
        return [code_block["class"][-1].capitalize()]
    else:
        return get_user_decision(soup, code_block)


def fetch_comments(article):
    """Get all the comments for an article and process their languages.
    Use the cache if possible.  A comment can have more than one 
    language associated with it.
    """
    result = requests.get("https://dev.to/api/comments",
                            params={"a_id": article["id"]})
    if result.status_code != 200:
        raise ValueError("Couldn't get comments for article.", article)
    data = result.json()

    for comment in data:
        if comment["id_code"] in article["comments"]:
            continue

        languages = parse_comment(comment)
        article["comments"][comment["id_code"]] = languages


def fetch(config):
    """Fetch Subcommand.  Download and process all new comments.

    Config has a few options:
    - history_file: the file to get the cache out of and save it 
                    back into.  Defaults to `aoc_language_bot_history.json`.
    - url_file: the file to get the list of article URLs from.  Defaults
                to `urls.txt`.
    - delete: boolean flag.  If true, blows away the current database.
    """
    try:
        with open(config.history_file, "r") as hf:
            history = json.load(hf)
    except FileNotFoundError:
        logging.warning("No history file found.  Creating a new one.")
        history = {}

    if config.delete:
        logging.info("Cleared history.")
        history = {}
    
    with open(config.url_file, "r") as uf:
        urls = uf.read().splitlines()

    get_article_ids(urls, history)

    for article in history.values():
        time.sleep(1)  # Good citizen award
        logging.info(f"Fetching comments for day {article['day']}.")
        fetch_comments(article)

    with open(config.history_file, "w") as hf:
        logging.info("Saving history file.")
        json.dump(history, hf, indent=2)


def show_markdown(article, aliases):
    """Output the markdown "updated at" time and table for that day."""
    now = datetime.now()
    print(f"Updated {now.strftime('%I:%M%p %m/%d/%Y')} PST.\n")

    all_languages = chain.from_iterable(article["comments"].values())
    languages = Counter([lang for lang in all_languages if lang != "None"])
    
    print("| Language   | Count |")
    print("|------------|-------|")
    
    for language, count in languages.most_common():
        if language in aliases:
            language = aliases[language]
        print(f"| {language:10} | {count:5} |")

def show(config):
    """Show Subcommand.  Output Markdown for copy/paste tallying the
    langs.

    Config has a few options:
    - day: the integer number of the day to output (1-25 inclusive).
    - history_file: the file to get the cache out of and save it 
                    back into.  Defaults to `aoc_language_bot_history.json`.
    - url_file: the file to get the list of article URLs from.  Defaults
                to `urls.txt`.
    - alias_file: A file of key/values for replacements for common
                  misspellings.  Defaults to `aliases.json`.
    """
    try:
        with open(config.history_file, "r") as hf:
            history = json.load(hf)
    except FileNotFoundError:
        logging.error("No history file found.")
        exit(1)

    try:
        with open(config.alias_file, "r") as af:
            aliases = json.load(af)
    except FileNotFoundError:
        logging.warning("No aliases file found.  Using an empty one."
                        "  Create 'aliases.json' in your directory if desired.")
        aliases = dict()

    for article in history.values():
        if article["day"] == config.day:
            show_markdown(article, aliases)
            break
    else:
        logging.error(f"Couldn't find {config.day}.")


def main():
    parser = argparse.ArgumentParser(description="Tabulate Advent of Code comments.")
    parser.add_argument("-u", "--url_file",
        help="File path to list of article URLS.",
        default="urls.txt"
    )
    parser.add_argument("-H", "--history_file",
        help="History database file to use as cache.",
        default="aoc_language_bot_history.json"
    )

    subparsers = parser.add_subparsers()
    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.add_argument("-d", "--delete",
        help="Overwrites the existing history file.",
        action='store_true'    
    )
    fetch_parser.set_defaults(func=fetch)
    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("day", help="The day to output a table for.", type=int)
    show_parser.add_argument("-a", "--alias_file",
        help="A file that lists proper spellings for things the autospeller gets wrong.",
        default="aliases.json"
    )
    show_parser.set_defaults(func=show)

    args = parser.parse_args()

    try:
        args.func(args)
    except AttributeError:
        parser.parse_args(["-h"])

if __name__ == "__main__":
    main()