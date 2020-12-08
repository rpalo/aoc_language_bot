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