#!/usr/bin/env python3

# pocketsnack - KonMari your Pocket tsundoku from the command line
# Copyright (C) 2018 - 2021 Hugh Rundle

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# You can contact Hugh on email hugh [at] hughrundle [dot] net
# or Mastodon at @hugh@ausglam.space

# ----------------
# Import libraries
# ----------------

from argparse import ArgumentParser
from rich.console import Console
from rich.theme import Theme
import yaml

# bundled with Python
import os
import pkg_resources
import subprocess

# local modules
from pocketsnack import toolkit as pt

# set up rich
custom_theme = Theme({
    "highlight" : "color(255) on cyan",
    "command": "red on white"
})
console = Console(theme=custom_theme, highlight=False)

# define config filepath for all platforms
conf_file_path = os.path.join('~', '.pocketsnack_conf.yml')
config_file = os.path.expanduser(conf_file_path)

  # ----------------
  # What happens with each command?
  # ----------------

def main():

  try:

    # Find all args that have a value other than False
    # This helps with error messages for optional args 
    # that need to be used in combination with something else
    true_vars = []
    orphans = ['list', 'archive', 'all', 'since', 'before']
    for x in vars(options):
      if vars(options)[x]:
        true_vars.append(x)

    if S['pocket_consumer_key'] == 'YOUR_KEY_HERE':
      console.print('\n  :exclamation_mark: You have not set a [command] pocket_consumer_key [/command] in your configuration file. Run [highlight] pocketsnack --config [/highlight] or check the README for help.')

    if options.config:
      conf = pt.config(config_file)
      console.print(conf)

    elif options.authorise:
      # Run authorise once first to retrieve a pocket_access_token
      auth = pt.authorise(config_file, consumer_key)
      console.print(auth or "  [bold red on color(255)] Authorisation cancelled ")

    elif options.dedupe:
      if options.tbr:
        state = "archive"
        tag = S['archive_tag']
      else:
        state = "archive" if options.archive else "all" if options.all else "unread"
        tag = False
      
      location = tag if tag else state if state != 'unread' else 'list'
      console.print('  [highlight] Checking for duplicates in ' + location + ' [/highlight]')
      pt.dedupe(state, tag, S['fave_dupes'], consumer_key, access_token)

    elif options.lucky_dip:
      console.print('  [highlight] Running lucky dip... [/highlight]')
      dip = pt.lucky_dip(
        consumer_key, 
        access_token, 
        S['archive_tag'], 
        S['items_per_cycle'], 
        S['num_videos'], 
        S['num_images'], 
        S['num_longreads'], 
        S['longreads_wordcount'], 
        options.before, 
        options.since)
      console.print(dip)

    elif options.info:

      def print_info(response, collection):
        items = str(len(response))
        longreads = 0
        for item in response:
          # is it a long read?
          if 'word_count' in response[item]:
            words = int(response[item]['word_count'])
            longread = True if  words > S['longreads_wordcount'] else False
          else:
            longread = False
          if longread:
            longreads += 1

        if options.before:
          console.print(collection + 'has ' + items + ' items ' + 'updated prior to ' + str(options.before) + ' days ago and ' + str(longreads) + ' are longreads.')
        elif options.since:
          console.print(collection + 'has [highlight] ' + items + ' [/highlight] items ' + 'updated since ' + str(options.since) + ' days ago and ' + str(longreads) + ' are longreads.')
        else:
          console.print(collection + 'has [highlight] ' + items + ' [/highlight] items and [highlight] ' + str(longreads) + ' [/highlight] are longreads.')

      if options.archive:
        response = pt.info(consumer_key, access_token, archive_tag, options.before, options.since)
        if len(response) > 0:
          print_info(response, '  The TBR archive ')
        else:
          console.print('  No items match that query')

      elif options.list:
        response = pt.info(consumer_key, access_token, False, options.before, options.since)
        if len(response) > 0:
          print_info(response, '  The user List ')
        else:
          console.print('  No items match that query')

      else:
        console.print('\n [command] --info [/command] requires a second argument ([command]-a[/command] or [command]-l[/command]). Check [command] pocketsnack --help [/command] for more information\n')

    elif options.purge:

      if options.list:
        console.print('  [highlight] Purging tags in the list [/highlight]')
        purge = pt.purge_tags(
          'unread', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        console.print(purge)

      elif options.archive:
        console.print('  [highlight] Purging tags in the archive [/highlight]')
        purge = pt.purge_tags(
          'archive',
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        console.print(purge)

      elif options.all:
        console.print('  [highlight] Purging tags in both the archive and the list [/highlight]')
        purge = pt.purge_tags(
          'all', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        console.print(purge)

      elif options.tbr:
        console.print('  [highlight] Purging tags in tbr archive [/highlight]')
        purge = pt.purge_tags(
          'tbr', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        console.print(purge)

      else:
        console.print('\n  [highlight] --purge [/highlight] requires a second argument (-a, -l or -b). Check [highlight] pocketsnack --help [/highlight] for more information\n')

    elif options.stash:
      stash = pt.stash(
        consumer_key, 
        access_token, 
        archive_tag, 
        S['replace_all_tags'], 
        retain_tags, 
        S['ignore_faves'], 
        ignore_tags, 
        options.before, 
        options.since)
      console.print(stash)

    elif options.test:
      result = pt.test(consumer_key, access_token)
      console.print(result)
    
    elif options.version:
      # version number from package info
      vnum = pkg_resources.require("pocketsnack")[0].version
      print(vnum)

    elif set(true_vars).intersection(orphans):
      console.print('\n   That command cannot be used by itself. Check [highlight] pocketsnack --help [/highlight] for more information\n')

    else:
      console.print('  [highlight] pocketsnack [/highlight] requires commands and/or flags to do anything useful. Try [highlight] pocketsnack -h [/highlight] for more information')

  except (NameError, FileNotFoundError):
    # this happens when there is no config file
    # since we already provide an error message below
    # we do nothing here
    pass

  except ValueError:
    console.print("  :flushed_face: Whoops, looks like there is a problem with your config file. Try [highlight] pocketsnack --config [/highlight] to fix this")

# -----------------------------------
# Parse commands (the action is here)
# -----------------------------------
try:

  configyaml = open(config_file, 'r')
  for S in yaml.safe_load_all(configyaml):

    # ----------------
    # Settings
    # ----------------

    # assign short variable names from the config file
    access_token = S['pocket_access_token']
    consumer_key = S['pocket_consumer_key']
    archive_tag = S['archive_tag']
    ignore_tags = set(S['ignore_tags'])
    retain_tags = set(S['retain_tags'])

    # ----------------
    # argparser arguments
    # ----------------

    parser = ArgumentParser(description='pocketsnack: KonMari your Pocket tsundoku from the command line')
    admin = parser.add_argument_group('admin commands')
    actions = parser.add_argument_group('action commands')
    mex = parser.add_mutually_exclusive_group()
    timers = parser.add_mutually_exclusive_group()

    mex.add_argument(
        "-a", "--archive", action="store_true", help="get information on TBR items in archive (with -i) or purge tags in archive (with -p)"
    )
    mex.add_argument(
        "-b", "--all", action="store_true", help="purge all tags in both list and archive (with -p) or dedupe both list and archive (with --dedupe)"
    )
    actions.add_argument(
        "-c", "--config", action="store_true", help="create or edit your config file stored at ~/.pocketsnack_conf.yml"
    )
    actions.add_argument(
        "-d", "--lucky_dip", action="store_true", help="move random items tagged 'tbr' from archive to list, depending on config"
    )
    actions.add_argument(
        "--dedupe", action="store_true", help="de-duplicate list (-l), archive (-a), tbr items (--tbr) or all (-b). Defaults to list"
    )
    actions.add_argument(
        "-i", "--info", action="store_true", help="get information on items in list or TBR items in archive"
    )
    mex.add_argument(
        "-l", "--list", action="store_true", help="get information on items in list (with -i) or purge tags in list (with -p)"
    )
    timers.add_argument(
        "-n", "--since", type=int, help="only act on items where last activity is newer than a given number of days. Use with any action command"
    )
    timers.add_argument(
        "-o", "--before", type=int, help="only act on items where last activity is older than a given number of days. Use with any action command"
    )
    actions.add_argument(
        "-p", "--purge", action="store_true", help="remove all tags from list, archive, or both, depending on the second argument provided and excepting tags listed in 'retain_tags' in config"
    )
    actions.add_argument(
        "-s", "--stash", action="store_true", help="add 'tbr' tag to all items in user list and archive them, with exceptions as per config"
    )
    admin.add_argument(
        "-t", "--test", action="store_true", help="test whether API call returns data"
    )
    mex.add_argument(
        "--tbr", action="store_true", help="used in conjuction with --dedupe to dedupe only items in the tbr archive"
    )
    admin.add_argument(
        "-u", "--authorise", action="store_true", help="authorise app to connect to a Pocket account"
    )
    admin.add_argument(
        "-v", "--version", action="store_true", help="print the current version number to screen"
    )

    options = parser.parse_args()
    configyaml.close() # we don't need to leave this open: if we do, Windows can't "authorise"

  if __name__ == '__main__':

    main()

except FileNotFoundError:
  console.print(' [highlight] pocketsnack [/highlight] needs a config file!')
  user_input = input('  Do you want to create one now using your default text editor (y/n)?')
  if user_input in ["y", "yes", "Y", "Yes", "YES"]:
    conf = pt.config(config_file)
    console.print(conf)
  else:
    console.print('  Some other time then.')
