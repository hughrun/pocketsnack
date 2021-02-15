# KonMari your Pocket tsundoku from the command line

`pocketsnack` is a command line application offering various commands to make your [Pocket](https://getpocket.com) account more manageable. You can de-duplicate your list, purge unwanted tags, and hide your enormous 'to be read' list in a special archive so that looking at it doesn't become paralysing. Tested on MacOS, Ubuntu Linux and Windows 10. Expected to run on other platforms.

This is the version 3.x documentation. If you prefer to use an older version you can still read the [version 2 README](v2_README.md) or [version 1 README](v1_README.md).

## Requirements

* Python 3.6.1 or higher
* `xdg-utils` (on Linux & BSD)
* A web browser to obtain a Pocket token

## tl;dr

1. make sure you have installed Python version 3.6.1 or higher.
2. `pip install pocketsnack` (you may need to use `pip3` instead)
3. `pocketsnack --config`
4. Add your Pocket API consumer key to the config file
5. `pocketsnack --authorise`
6. You are now ready to enjoy using pocketsnack from any directory

## Getting started

### Creating a Pocket consumer key for your app

1. Log in to Pocket in a web browser
2. Go to [`https://getpocket.com/developer`](https://getpocket.com/developer) and click 'CREATE NEW APP'
3. Complete the form: you will need all permissions, and the platform should be _Desktop (other)_ or _Mac_.
4. Your new app will show a **consumer key**, which you need to paste into the first line in your configuration file.

### Creating a configuration file

Before you can use `pocketsnack` you need to create a configuration file. If you run any command (including simply `pocketsnack` without an argument) when your configuration file doesn't exist, a new file will be created and will open in your default application for editing `yaml` files. You *must* copy in the consumer key referred to above, and *may* adjust any other settings. 

You can adjust most settings, but the defaults should be sensible for most users if you just want to get started.

| setting              | type    | description                           |  
| :------------------- | :---:   | :------------------------------------ |  
| pocket_consumer_key  | string  | the consumer key provided by Pocket when you register your 'app' (see below)|
| items_per_cycle      | integer | how many items you want to bring in to the List from your `tbr` archive when using `--lucky_dip`|
| archive_tag          | string  | the tag to use to identify items in your 'to be read' archive|
| ignore_tags          | list    | a list of tag names - items with any of these tags will be ignored by `--stash` and remain in your Pocket List|
| ignore_faves         | boolean | if set to `true` favorited items will be ignored by `--stash` and remain in your Pocket List| 
| fave_dupes         | boolean | if set to `true` the remaining (original) item will be favorited when duplicates are removed with `--dedupe`| 
| replace_all_tags     | boolean | if set to `true` all tags will be removed by `--stash` when adding the `archive_tag`, except anything in `retain_tags`|
| retain_tags          | list    | a list of tag names - these tags will not be removed by `--purge`, nor by `--stash` if `replace_all_tags` is set to `true`|
| longreads_wordcount  | integer | determines how long a 'longread' is. |
| num_videos           | integer | how many videos (if there are videos in your list) should be included in each `--lucky_dip`. This is a subset of `item_per_cycle`, not in addition to the total.|
| num_images           | integer | how many images (if there are images in your list) should be included in each `--lucky_dip`. This is a subset of `item_per_cycle`, not in addition to the total.|
| num_longreads        | integer | how many long reads (if there are long reads in your list) should be included in each `--lucky_dip`. This is a subset of `item_per_cycle`, not in addition to the total. The definition of a long read is determined by `longreads_wordcount`|
| pocket_access_token  | string  | access token required to interact with the Pocket API. This will be updated when you run `--authorise` and should not be edited manually.|

Save and close when you're done. You can edit this file again at any time by running `pocketsnack --config`.

### Authorising your app with a Pocket access token

Pocket uses OAuth to confirm that your app has permission from your user account to do things in your account. This means you need to authorise the app before you can do anything else. Once you have copied your app consumer key into the config file, run `pocketsnack --authorise` to get your token.

You should now have a line a value for `pocket_access_token:` that looks something like `'aa11bb-zz9900xx'`

## Usage

To run commands, use `pocketsnack [command]`.

### -h, --help

Outputs help for each command

## admin commands

### -t, --test

Outputs the full JSON from the first article returned by a call to the API. Normally you will never need to use this.

### -u, --authorise

This command has an 's', not a 'z', and the short version is a 'u', not an 'a'.

You need this to authorise your app. Everything else works exclusively on the command line, but _authorise_ needs to open a browser to complete the authorisation process, so you need to run this on a machine with a web browser. It will authorise your app with your user, wait for you to confirm that you have completed the authorisation (by typing 'done') and then add the token to your config file. You also need to run `--authorise` if you want to change the Pocket account you are using with `pocketsnack`.

## -v, --version

Prints the current version number to screen.

## action commands

### -c, --config

Create or edit your config file which is stored at `~/.pocketsnack_conf.yml`.

### --dedupe

Removes duplicates from your List, TBR archive, full Archive, or everything, depending on the flag you use with it. This is an extension of the functionality provided by [pickpocket](https://github.com/hughrun/pickpocket).

### -d, --lucky_dip

Returns items with the archive tag from the archive to the list, and removes the archive tag. The number of items returned is determined by `items_per_cycle` in `settings.yaml`. Note that if `num_videos` and `num_images` add up to more than `items_per_cycle`, then `--lucky_dip` will only return the total specified in `items_per_cycle`. Videos take precedence.

### -i, --info LOCATION

Get information on items in a list (if LOCATION is `-l`) or TBR items in your archive (if LOCATION is `-a`).

### -p, --purge

You can use `--purge` to clear all tags in your List, TBR achive, full Archive, or everything -  excluding the `archive_tag` and any `retain_tags`. This is useful if you've been using the _Aus GLAM Blogs_ Pocket tool or anything else that retains the original tags from articles.

`--purge` requires a second argument: `--list`, `--tbr`, `--archive`, or `--all`, depending on where you want to purge tags.

### -s, --stash

Adds the archive tag to everything in your list, and then archives them. Depending on the value of `ignore_faves` and `ignore_tags` in `settings.yaml`, and any before/since values, some items may be excluded and remain in the List.

## optional flags

### -a, --archive

Used in combination with `--info`, this tells you how many items are in your archive and how many of them are 'long reads'. You can set the wordcount defining a long read in your config. 

Used with `--purge`, it purges tags on items in the archive.

Used with `--dedupe`, it restricts de-duplication to the full Pocket Archive.

### -l, --list

Same as _archive_ but for your Pocket List instead of your archive.

### --tbr

Used in conjuction with `--dedupe` to dedupe only items in the `tbr` archive.

Used with `--purge`, it purges tags only on items in the `tbr` archive.

### -b, -all

For use with `--purge` - purge tags from your entire Pocket account.

Used with `--dedupe`, it de-duplicates your entire Pocket account.

### -n, --since SINCE

Restrict the current _action command_ to only items updated more recently than _SINCE_ number of days.

### -o, --before BEFORE

Restrict the current _action command_ to only items updated less recently than _BEFORE_ number of days.

### What does 'updated' mean?

The Pocket API does not store a value for the date an items was first added. The only value we can get is _since_, which is a timestamp updated every time there is a change made to an item via or equivalent to any `add` or `modify` [API action](https://getpocket.com/developer/docs/overview). This could be when it is added to the List, move to the archive, moved out of the archive back into the List, or has changes made to tags (even if that tag update results in no actual change - i.e. if `--purge` has been run against the item, regardless of whether it had any tags to begin with).

## Examples

Find out how many `TBR` items are in the archive:

`pocketsnack --info -a`

Stash only items updated in the last 2 days:  

`pocketsnack --stash -n 2`

Stash only items NOT updated in the last 7 days:  

`pocketsnack --stash -o 7`

Purge tags on all items in the List that were updated in the last day:

`pocketsnack -pln 1`

Run lucky_dip:

`pocketsnack --lucky_dip`

Run lucky_dip but only choose from items last updated longer ago than one week:

`pocketsnack -d -o 7`

## A note on version 3

Version 3.x introduces a new YAML format for the settings file. This approach also allows for changes to the settings file without having to re-install `pocketsnack`, which was an unintended side effect of the previous approach.

## Uninstalling or moving v1 script to a new directory

### If you installed with pip

Run `pip uninstall pocketsnack` or `pip3 uninstall pocketsnack`.

### If you installed using the legacy version 1 install.sh script

1. Delete the executable link, e.g. `rm /usr/local/bin/pocketsnack`  

   If you don't do this when re-installing in a different directory, running `pocketsnack` will fail because it will still be pointing at the old directory.
2. Now you can safely delete the pocket-snack directory: `rm -r pocketsnack`

## Bugs and suggestions

Please log an issue - but check the existing issues first in case it's already been/being dealt with.
