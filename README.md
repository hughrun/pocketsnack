# pocket-snack
When your Pocket list is overwhelming, pocket-snack lets you see just what you can read today

## A note on version 2

All commands have changed since version 1 - read the _Usage_ section carefully. This was necessary in order to provide better functionality without making the code too confusing.

One of the changes is that the `refresh` command from version 1 no longer exists. This is so that `--since`, and `--before` can be used with both `--stash` and `lucky_dip`. If you want replicate `refresh` you simply need to run `--stash` followed by `--lucky_dip`. From the command line you could do:
```bash
pocketsnack -s && pocketsnack -d
```
The automation of `pocketsnack refresh` has _also_ been removed. This didn't really work very consistently, and was causing a lot of maintenance headaches. I'm looking at how to bring it back in a different way, but for now it's been removed.

## Getting started

### Quick version

1. make sure you have installed Python 3 and it is callable with `python3`
2. copy `settings-example.py` to `settings.py`
3. create Pocket app and paste consumer key into `settings.py`
4. run `bash install.sh` and follow the prompts

### Dependencies

You will need Python 3.x installed and it must be called by `python3`, rather than `python`. These instructions, and the install script, assume you are using a Unix-like (Linux, BSD, MacOS) operating system. Microsoft Windows is not currently supported.

On MacOS the easiest thing to do is to [install Python 3 using Homebrew](https://docs.brew.sh/Homebrew-and-Python): `brew install python`.

The install script should install the `requests` module for you when you run `bash install.sh`. If you prefer, you can install it manually using **pip**: `pip3 install requests`

### Settings

You will need to copy **settings-example.py** to a new file called **settings.py** before you start. You can do this however you like, but from the command line you could use `cp settings-example.py settings.py`, and then edit it with a text editor like `nano`.

You can adjust most settings, but the defaults in **settings-example.py** should be ok for most users. Check the comments in **settings.example.py** for an explanation of each setting.

### Creating a Pocket consumer key for your app

1. Log in to Pocket in a web browser
2. Go to https://getpocket.com/developer and click 'CREATE NEW APP'
3. Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
4. Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

### Pocket access token

Pocket uses OAuth to confirm that your app has permission from your user account to do stuff in your account. This means you need to authorise the app before you can do anything else. Once you have copied you app consumer key into settings.py, when you run the `install.sh` bash script, this will run `authorise` for you. If you prefer to install manually, or want to change the Pocket account details, you should run `pocketsnack --authorise` to get your token (see below).

You should now have a line at the bottom of settings.py saying something like `pocket_access_token = 'aa11bb-zz9900xx'`

## Usage

To run commands, use `pocketsnack [command]`.

### -h, --help

Outputs help for each command

## admin commands

### -t, --test

Outputs the first article returned by a call to the API. Normally you will never need to use this.

### -u, --authorise

This command has an 's', not a 'z', and the short version is a 'u', not an 'a'.

You need this to authorise your app. This command is automatically run by `install.sh`. Everything else works exclusively on the command line, but _authorise_ needs to open a browser to complete the authorisation process, so you need to run this on a machine with a web browser. It will authorise your app with your user, wait for you to confirm that you have completed the authorisation (by typing 'done') and then add the token to `settings.py`. Use it if you want to change the Pocket account you are using with pocketsnack.

## action commands

### -d, --lucky_dip

Returns items with the archive tag from the archive to the list, and removes the archive tag. The number of items returned is determined by `items_per_cycle` in `settings.py`. Note that if `num_videos` and `num_images` add up to more than `items_per_cycle`, _lucky_dip_ will only return the total specified in `items_per_cycle`. Videos take precedence.

### -p, --purge

You can use **purge_tags** to clear all tags in your List, Archive, or both, excluding the `archive_tag` and any `retain_tags`. This is useful if you've been using the Aus GLAM Blogs Pocket tool or anything else that retains the original tags from articles.

`purge_tags` requires a second argument: `--list`, `--archive`, or `--all`, depending on where you want to purge tags.

### -s, --stash

Adds the archive tag to everything in your list, and then archives them. Depending on the value of `ignore_faves` and `ignore_tags` in `settings.py`, and any before/since values, some items may be excluded and remain in the List.

## optional flags

### -a, --archive

Used in combination with `--info`, this tells you how many items are in your archive and how many of them are 'long reads'. You can set the wordcount defining a long read in `settings.py`. Used with `--purge`, it purges tags on items in the archive.

### -l, --list

Same as _archive_ but for your list instead of your archive.

### -b, -all

For use with `--purge` - purge tags from _both_ the List and the Archive.

### -n, --since SINCE

Restrict the current _action command_ to only items updated more recently than _SINCE_ number of days,

### -o, --before BEFORE

Restrict the current _action command_ to only items updated less recently than _BEFORE_ number of days,

## Uninstalling or moving to a new directory

Don't like _pocket-snack_ any more or want to re-install it in a new directory? No problem, you will just need to do a little maintenance:

1. Delete the executable link - if you don't do this when re-installing in a different directory, running `pocketsnack` will fail because it will still be pointing at the old directory.

   `rm /usr/local/bin/pocketsnack`

2. Now you can safely delete the pocket-snack directory.

## Bugs and suggestions

Please log an issue - but check the existing issues first in case it's already been/being dealt with.