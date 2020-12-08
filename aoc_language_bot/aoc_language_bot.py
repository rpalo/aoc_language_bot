import argparse
from collections import Counter
from itertools import chain
import json
import sys
from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup

def get_article_ids(urls, history):
    for day, url in enumerate(urls, start=1):
        if url in history:
            continue
        time.sleep(1)
        protocol, domain, user_slug = url.partition("dev.to/")
        api_url = protocol + domain + "api/articles/" + user_slug
        # print(api_url)
        result = requests.get(api_url)
        if result.status_code != 200:
            print(f"Couldn't get {url} ID.", file=sys.stderr)
            continue
        # print(result.text)
        data = result.json()
        # print(data)
        history[url] = {
            "id": data["id"],
            "title": data["title"],
            "day": day,
            "comments": dict(),
        }


def get_user_decision(soup, code_block):
    print("Need input.", soup.prettify(), sep="\n")
    while True:
        language = input("Language (<Enter> for None): ") or "None"
        confirm = input(f"Confirm you meant '{language}' (y/n): ")
        if confirm in ['y', 'Y']:
            return [lang.capitalize() for lang in language.split('/')]


def parse_comment(comment):
    soup = BeautifulSoup(comment["body_html"], "html.parser")
    code_block = soup.find("pre", class_="highlight")

    # TODO: Check to see if the comment contains any language names from a list

    if code_block != None and code_block["class"][-1] != "plaintext":
        return [code_block["class"][-1].capitalize()]
    else:
        return get_user_decision(soup, code_block)

def fetch_comments(article):
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
    try:
        with open(config.history_file, "r") as hf:
            history = json.load(hf)
    except FileNotFoundError:
        history = {}

    if config.delete:
        history = {}
    
    with open(config.url_file, "r") as uf:
        urls = uf.read().splitlines()

    get_article_ids(urls, history)

    for article in history.values():
        time.sleep(1)
        fetch_comments(article)

    with open(config.history_file, "w") as hf:
        json.dump(history, hf, indent=2)


def show_markdown(article, aliases):
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
    with open(config.history_file, "r") as hf:
        history = json.load(hf)

    try:
        with open(config.alias_file, "r") as af:
            aliases = json.load(af)
    except FileNotFoundError:
        aliases = dict()

    for article in history.values():
        if article["day"] == config.day:
            show_markdown(article, aliases)
            break
        else:
            print("Couldn't find that day.")


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
    args.func(args)

if __name__ == "__main__":
    main()