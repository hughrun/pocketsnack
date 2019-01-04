# pocket-snack
When your Pocket list is overwhelming, pocket-snack lets you see just what you can read today

The basic idea is that each time the script runs it moves everything in `My List` to `Archive` with a `TBR` tag, then randomly selects X number of items to go back into `My List` so that instead of an overwhelming number of things to be read, you just have the number you can comfortably expect to read per cycle (day, week etc).

This is very much work in progress, but you can play with the basic functionality now.

## Usage

To run, use `python3 main.py [command]`

If you're using it regularly, you probably want to run `python3 main.py stash` followed by `python3 main.py lucky_dip`

## Creating an app in Pocket

1. Log in to Pocket in a web browser
2. Go to https://getpocket.com/developer and click 'CREATE NEW APP'
3. Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
4. Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

## commands

### archive

This tells you how many items are in your archive and how many of them are 'long reads'. You can set the wordcount defining a long read in `settings.py`.

### authorise

This has an 's', not a 'z'.

You need this to authorise your app. Everything else works exclusively on the command line, but _authorise_ needs to open a browser to complete the authorisation process, so you need to run this on a machine with a web browser. It will authorise your app with your user, and add the token to `settings.py`.

### list

Same as _archive_ but for your list instead of your archive.

### lucky_dip

Returns items from the archive to the list, and removes the archive tag. The number of items returned is determined by `items_per_cycle` in `settings.py`. Note that if `num_videos` and `num_images` add up to more than `items_per_cycle`, _lucky_dip_ will only return the total specified in `items_per_cycle`. Videos take precedence.

### stash

Adds the archive tag to everything in your list, and then archives them. Depending on the value of `ignore_faves` and `ignore_tags` in `settings.py` favorited \[sic] items may remain in the List.

## Bugs and suggestions

Log an issue - but check the existing issues first in case it's already been/being dealt with.