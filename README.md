# pocket-snack
When your Pocket list is overwhelming, pocket-snack lets you see just what you can read today

Each time the `refresh` command runs, it moves everything in `My List` to `Archive` with a particular tag, then randomly selects X number of items with that tag to go back into `My List` so that instead of an overwhelming number of things to be read, you just have the number you can comfortably expect to read per cycle (day, week etc).

This is a work in progress, but all functions described here should be working.

## Getting started

### tl;dr

1. install python 3 and the _requests_ module
2. copy `settings-example.py` to `settings.py`
3. create Pocket app and paste consumer key into settings.py
4. run `bash install.sh` and follow the prompts

### Dependencies
You will need Python 3.x installed and it must be called by `python3`, rather than `python`. These instructions, and the install script, assume you are using a Unix-like (Linux, BSD, MacOS) operating system. Microsoft Windows is not currently supported.

On MacOS the easiest thing to do is to [install Python 3 using Homebrew](https://docs.brew.sh/Homebrew-and-Python): `brew install python`.

Then install the Python **requests** module using **pip**: `pip3 install requests`

### Settings

You will need to copy **settings-example.py** to a new file called **settings.py** before you start. You can do this however you like, but from the command line you could use `cp settings-example.py settings.py`, and then edit it with a text editor like `nano`.

You can adjust most settings, but the defaults in **settings-example.py** should be ok for most users. Check the comments in **settings.example.py** for an explanation of each setting.

### Creating a Pocket consumer key for your app
1. Log in to Pocket in a web browser
2. Go to https://getpocket.com/developer and click 'CREATE NEW APP'
3. Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
4. Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

### Pocket access token

Pocket uses OAuth to confirm that your app has permission from your user account to do stuff in your account. This means you need to authorise the app before you can do anything else. Once you have copied you app consumer key into settings.py, when you run the `install.sh` bash script, this will run `authorise` for you. If you are doing everything manually you should run `pocketsnack authorise` to get your token (see below).

You should now have a line at the bottom of settings.py saying something like `pocket_access_token = 'aa11bb-zz9900xx'`

## Usage

For most users you simply need to run `install.sh` and then forget about it. The install script will ask a series of questions, authorise your app, and optionally set up a daily or weekly task to refresh your list. On MacOS this is done via **launchd** and on Linux via **cron**. If you want to use cron instead of launchd on Mac, just choose 'Linux' when asked - but I wouldn't recommend it (read on for why).

In both cases, `pocketsnack refresh` will run at the specified time. In the case of **cron**, this will only happen if the machine is up and logged on - e.g. a server. In the case of **launchd**, the script will be associated with your user account. If your machine is sleeping or your account logged out at the scheduled time, it will run immediately when you wake the machine up or log in. This allows you to set it for, e.g. 5am and be confident that when you open your Macbook at 7am the script will run and your Pocket account will refresh.

If you use launchd, log files for stdout and errors will be created wherever you saved _pocketsnack_.

To run commands manually, use `pocketsnack [command]`.

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

Runs `stash` followed by `lucky_dip`. This is the command that is run by launchd or cron if you set it up using `install.sh`.

### stash

Adds the archive tag to everything in your list, and then archives them. Depending on the value of `ignore_faves` and `ignore_tags` in `settings.py` some items may remain in the List.

## Bugs and suggestions

Please log an issue - but check the existing issues first in case it's already been/being dealt with.