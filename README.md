# Advent of Code DEV Megathread Language Bot

In 2019, on the DEV megathread for the Advent of Code challenge, the
thread author kept a tally of how many people had completed the previous
day's challenge in each language.

I'm doing the same thing now, but updating them is quickly becoming
more time consuming than planned.  It's time for a bot!

## The Idea

For each article in my DEV AoC megathread, this bot should go get the
comments, and, ideally, output the markdown table that I can copy paste
into the article.

There are some comments that don't have code blocks classified by language.
And some people comment just that they solved in particular language,
maybe with an image of their code.  In order to not duplicate work, the
bot should run each comment through a checker that checks for any
possible language words that might signify that there's more to the
prose of the article about how the person solved things.  It should
show me the text of the comment and ask me to classify the language.

Then it should save those decisions so it doesn't have to ask me again.

## Installation

The short version is clone the repo, create a virtual environment,
install the dependencies, and you're good to go.

```bash
git clone https://github.com/rpalo/aoc_language_bot.git
cd aoc_language_bot.git
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Currently two subcommands are supported: fetching and showing.

### Fetching

Fetching downloads the articles and comments and builds a database via
a semi-user-interactive mode.  Any comments it's not sure about, it'll
ask you what you think.  Answer with the language you think it is, and
if it's a comment that doesn't have a submission in it, leave your
answer blank.

```shell
python3 aoc_language_bot/aoc_language_bot.py fetch
```

By default, it expects a list of post URLs in the same directory you
call it from called `urls.txt`.  Each URL on its own line with no
other characters.  You can customize this file path with the `-u` flag.

```shell
python3 aoc_language_bot/aoc_language_bot.py -u data/my_urls.txt fetch
```

Similarly, it expects and subsequently force-creates a database file,
which is, by default called `aoc_language_bot_history.json`.  You can
customize this path with the `-H/--history_file` option.

```shell
python3 aoc_language_bot/aoc_language_bot.py -H data/db.json fetch
```

If the file doesn't exist, it will be created.

Note that both of these flags have to come before the `fetch` subcommand.

Also, you can use the `-d/--delete` flag to blow the existing database
away without having to hunt down and delete it yourself.

```shell
python3 aoc_language_bot/aoc_language_bot.py -H data/db.json fetch --delete
```

### Showing

The bot outputs the markdown into your terminal so you can copy/paste
it right into your blog post.

```shell
python3 aoc_language_bot/aoc_language_bot.py show 1
```

You must specify which day you wish to choose.  The order of the URLs
in the URL file specifies the days (i.e. the first URL is for Day 1).

You can optionally specify an "alias" file if the automated finder needs
correcting a lot.  By default, it expects a file called `aliases.json`
in the same directory you ran the command, but you can customize that
with the `-a/--alias_file` option.

```shell
python3 aoc_language_bot/aoc_language_bot.py show 1 -a data/nicks.json
```

Aliases are simple key-value pairs of common misspellings to how they
should properly look.  Here's an example:

```json
{
  "Javascript": "JavaScript",
  "Php": "PHP",
  "Csharp": "C#"
}
```

## Contributing

I welcome any contributions.  This was just a fun little project to make
my life a little easier, but I think it turned out good.  Feel free to 
fork it up, open a pull request, or open an issue to talk about improving
things.

## Code of Conduct

This project has a [Code of Conduct](CODE_OF_CONDUCT.md).  Please read it
before contributing or opening an issue.

## Development Notes

If someone makes two different language submissions in the same comment,
it will currently not be detected.  The auto finder should be extended
to compare all of the code blocks in the comment and do a hashset of
all of the languages included.
