# Read in a list of articles from a file

# Read in a previous saved history file.

# Get the article

# Get its ID

# Get the comments

# For each comment, check to see if it has a pre.highlight element.

# If so, store that as a language

# Check to see if the comment contains any language names from a list

# If so, or if it doesn't have a labeled code block, flag it for review
# If the saved history file says its already been reviewed, don't reflag it.

# Ask for a language.  I'll enter a language.  It'll save that decision
# for that comment to the saved history file.

# Output the Markdown table I need.

# Usage:
# - fetch (runs the process above)
# - show DAY (shows the Markdown table for DAY from history file)