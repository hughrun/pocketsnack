#!/usr/bin/env python3

# pocket-snack - a Python3 tool to help you retain your sanity when using your Pocket account

# Copyright (C) 2019  Hugh Rundle

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

# You can contact Hugh on Mastodon at @hugh@ausglam.space
# or Twitter at @hughrundle
# or email hugh [at] hughrundle [dot] net

# ----------------
# Import libraries
# ----------------

import requests
from argparse import ArgumentParser

# bundled with Python
from datetime import datetime
import json
import sys
import urllib
import webbrowser

# local modules
import settings
import pocket_toolkit as pt

# ----------------
# Settings
# ----------------

# TODO: clean this up

# assign short variable names from the settings file
consumer_key = settings.pocket_consumer_key
redirect_uri = settings.pocket_redirect_uri
archive_tag = settings.archive_tag

# settings dict for other vars
refresh_settings = [
  consumer_key,
  settings.pocket_access_token,
  archive_tag,
  settings.replace_all_tags,
  settings.retain_tags,
  settings.ignore_faves,
  settings.ignore_tags,
  settings.items_per_cycle,
  settings.num_videos,
  settings.num_images,
  settings.num_longreads,
  settings.longreads_wordcount
]

# ----------------
# argparser arguments
# ----------------

parser = ArgumentParser(description='\033[1;36mpocketsnack: a command line tool for decluttering your Pocket account\033[1;m')
admin = parser.add_argument_group('admin commands')
actions = parser.add_argument_group('action commands')
mex = parser.add_mutually_exclusive_group()
timers = parser.add_mutually_exclusive_group()

mex.add_argument(
    "-a", "--archive", action="store_true", help="get information on TBR items in archive (with -i) or purge tags in archive (with -p)"
)
mex.add_argument(
    "-b", "--all", action="store_true", help="purge all tags in both list and archive (with -p)"
)
actions.add_argument(
    "-d", "--lucky_dip", action="store_true", help="move random items tagged 'tbr' from archive to list, depending on settings"
)
actions.add_argument(
    "-i", "--info", action="store_true", help="get information on items in list or TBR items in archive"
)
mex.add_argument(
    "-l", "--list", action="store_true", help="get information on items in list (with -i) or purge tags in list (with -p)"
)
timers.add_argument(
    "-n", "--since", type=int, help="test whether API call returns data"
)
timers.add_argument(
    "-o", "--before", type=int, help="test whether API call returns data"
)
actions.add_argument(
    "-p", "--purge", action="store_true", help="remove all tags from list, archive, or both, depending on the second argument provided and excepting tags listed in 'retain_tags' in settings"
)
actions.add_argument(
    "-r", "--refresh", action="store_true", help="run 'stash' and then 'lucky_dip' in one operation"
)
actions.add_argument(
    "-s", "--stash", action="store_true", help="add 'tbr' tag to all items in user list and archive them, with exceptions as per settings"
)
admin.add_argument(
    "-t", "--test", action="store_true", help="test whether API call returns data"
)
admin.add_argument(
    "-u", "--authorise", action="store_true", help="authorise app to connect to a Pocket account"
)

options = parser.parse_args()

# ----------------
# What happens with each combination?
# ----------------

if __name__ == '__main__':

  # Find all args that have a value other than False
  # This helps with error messages for optional args 
  # that need to be used in combination with something else
  true_vars = []
  orphans = ['list', 'archive', 'all', 'since', 'before']
  for x in vars(options):
    if vars(options)[x]:
      true_vars.append(x)

  if options.authorise:
    # Run authorise once first to retrieve a pocket_access_token
    auth = pt.authorise(consumer_key, redirect_uri)
    print(auth)

  elif options.lucky_dip:
    print('\033[0;36mRunning lucky dip...\033[0;m')
    dip = pt.lucky_dip(consumer_key, settings.pocket_access_token, settings.archive_tag, settings.items_per_cycle, settings.num_videos, settings.num_images, settings.num_longreads, settings.longreads_wordcount)
    print('\033[0;36m' + dip + '\033[0;m')

  elif options.info:
    if options.archive:
      # Retrieve info about the user's list
      response = pt.get_tbr(consumer_key, settings.pocket_access_token, archive_tag)
      items = response['list']
      longreads = 0
      for item in items:
        # is it a long read?
        if 'word_count' in items[item]:
          words = int(items[item]['word_count'])
          longread = True if  words > settings.longreads_wordcount else False
        else:
          longread = False
        if longread:
          longreads += 1
      print('The TBR archive has ' + str(len(response['list'])) + ' items and ' + str(longreads) + ' are longreads.')

    elif options.list:
      # Retrieve info about the user's list
      response = pt.get_list(consumer_key, settings.pocket_access_token)
      items = response['list']
      longreads = 0
      for item in items:
        # is it a long read?
        if 'word_count' in items[item]:
          words = int(items[item]['word_count'])
          longread = True if  words > settings.longreads_wordcount else False
        else:
          longread = False
        if longread:
          longreads += 1
      print('The user list has ' + str(len(response['list'])) + ' items and ' + str(longreads) + ' are longreads.')

    else:
      print('\n   \033[0;36m--info\033[0;m requires a second argument (-a or -l). Check \033[0;36mpocketsnack --help\033[0;m for more information\n')

  elif options.purge:

    if options.list:
      print('\033[0;36mPurging tags in the list\033[0;m')
      purge = pt.purge_tags('unread', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

    elif options.archive:
      print('\033[0;36mPurging tags in the archive\033[0;m')
      purge = pt.purge_tags('archive', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

    elif options.all:
      print('\033[0;36mPurging tags in both the archive and the list\033[0;m')
      purge = pt.purge_tags('all', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

    else:
      print('\n   \033[0;36m--purge\033[0;m requires a second argument (-a, -l or -b). Check \033[0;36mpocketsnack --help\033[0;m for more information\n')

  elif options.refresh:
    print('Refreshing at ' + datetime.now().strftime('%a %d %b %Y %H:%M'))
    refresh = pt.refresh(*refresh_settings)
    print('\033[0;36m' + refresh + '\033[0;m')

  elif options.stash:
    stash = pt.stash(consumer_key, settings.pocket_access_token, archive_tag, settings.replace_all_tags, settings.retain_tags, settings.ignore_faves, settings.ignore_tags)
    print('\033[0;36m' + stash + '\033[0;m')

  elif options.test:
    result = pt.test(consumer_key, settings.pocket_access_token)
    print(result)
  
  #elif options.list or options.archive or options.all or options:
  elif set(true_vars).intersection(orphans):
    print('\n   That command cannot be used by itself. Check \033[0;36mpocketsnack --help\033[0;m for more information\n')

  else:
    print('\033[0;36mpocketsnack\033[0;m requires commands and/or flags to do anything useful. Try \033[0;36mpocketsnack -h\033[0;m for more information')