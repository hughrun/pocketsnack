# pocket-snack
When your Pocket list is overwhelming, pocket-snack lets you see just what you can read today

The basic idea is that each time the script runs it moves everything in `My List` to `Archive` with a `tbr` tag, then randomly selects X number of items to go back into `My List` so that instead of an overwhelming number of things to be read, you just have the number you can comfortably expect to read per cycle (day, week etc).

This is a work in progress, but the basic functionality should be working.

## Getting started

### tl;dr

1. copy settings-example.py to settings.py
2. create Pocket app and paste consumer key into settings.py
3. run `bash install.sh` and select '1' at the prompt

### Dependencies
You will need Python 3.x installed and it should be called by `python3`. These instructions assume you are using a Unix-like (Linux, BSD, MacOS) operating system.

The following Python modules need to be installed:

* requests

You should be able to install modules using pip with `pip3 install [module name]`

### Settings

You will need to copy settings-example.py to a new file called settings.py before you start. You can do this however you like, but from the command line you could use `cp settings-example.py settings.py`.

You can adjust most settings, but the defaults should be reasonable for most users.

### Creating a Pocket consumer key for your app
1. Log in to Pocket in a web browser
2. Go to https://getpocket.com/developer and click 'CREATE NEW APP'
3. Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
4. Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

### Pocket access token

Pocket uses OAuth to confirm that your app has permission from your user account to do stuff in your account. This means you need to authorise the app before you can do anything else. Once you have copied you app consumer key into settings.py, you should run `pocketsnack authorise` to get your token (see below). However, it you use the install.sh bash script, this will run `authorise` for you.

You should now have a line at the bottom of settings.py saying something like `pocket_access_token = 'aa11bb-zz9900xx'`

## Usage

To run, use `pocketsnack [command]`

If you're using it regularly, you probably want to run `pocketsnack stash` followed by `pocketsnack lucky_dip`. In an upcoming release this will be achieved by running the `refresh` command.

## commands

### archive

This tells you how many items are in your archive and how many of them are 'long reads'. You can set the wordcount defining a long read in `settings.py`.

### authorise

This has an 's', not a 'z'.

You need this to authorise your app. Everything else works exclusively on the command line, but _authorise_ needs to open a browser to complete the authorisation process, so you need to run this on a machine with a web browser. It will authorise your app with your user, wait for you to confirm that you have completed the authorisation (by typing 'done') and then add the token to `settings.py`.

### list

Same as _archive_ but for your list instead of your archive.

### lucky_dip

Returns items from the archive to the list, and removes the archive tag. The number of items returned is determined by `items_per_cycle` in `settings.py`. Note that if `num_videos` and `num_images` add up to more than `items_per_cycle`, _lucky_dip_ will only return the total specified in `items_per_cycle`. Videos take precedence.

### purge

This doesn't exist yet. It will delete all tags except for those specified in a list.

### refresh

This doesn't exist yet. It will run `stash` followed by `lucky_dip`.

### stash

Adds the archive tag to everything in your list, and then archives them. Depending on the value of `ignore_faves` and `ignore_tags` in `settings.py` some items may remain in the List.

## Bugs and suggestions

Log an issue - but check the existing issues first in case it's already been/being dealt with.