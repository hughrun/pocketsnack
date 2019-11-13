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

parser = ArgumentParser(description='pocketsnack: a command line tool for decluttering your Pocket account')
subparsers = parser.add_subparsers(help='for more help on these options use [command] --help (e.g. purge --help)')

parser.add_argument(
    "-a", "--archive", action="store_true", help="return data about items tagged 'tbr' in user's Pocket archive"
)
parser.add_argument(
    "-u", "--authorise", action="store_true", help="authorise app to connect to a Pocket account"
)
parser.add_argument(
    "-l", "--list", action="store_true", help="return data about items in user's Pocket list"
)
parser.add_argument(
    "-d", "--lucky_dip", action="store_true", help="move random items tagged 'tbr' from archive to list, depending on settings"
)
parser.add_argument(
    "-r", "--refresh", action="store_true", help="run 'stash' and then 'lucky_dip' in one operation"
)

# stash
# TODO: this needs to work like 'purge' with optional args to stash only items added more recently than X days or alternatively only items less recent than X days
# we also need this functionality for 'refresh' - maybe can use 'parents' option in argparse?

parser.add_argument(
    "-s", "--stash", action="store_true", help="add 'tbr' tag to all items in user list and archive them, with exceptions as per settings"
)
parser.add_argument(
    "-t", "--test", action="store_true", help="test whether API call returns data"
)
# purge
purge_choice = subparsers.add_parser(
  "purge", help="remove all tags from list, archive, or both ('all'), depending on the second argument provided and excepting tags listed in 'retain_tags' in settings.py. Defaults to 'list' if no argument is provided"
)
purge_choice.add_argument(
    'purge_choice', default='list', const="list", nargs='?', choices=('list', 'archive', 'all'), help="remove all tags from list, archive, or both"
)

options = parser.parse_args()

if __name__ == '__main__':

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

  if options.authorise:
    # Run authorise once first to retrieve a pocket_access_token
    auth = pt.authorise(consumer_key, redirect_uri)
    print(auth)

  if options.lucky_dip:
    print('\033[0;36mRunning lucky dip...\033[0;m')
    dip = pt.lucky_dip(consumer_key, settings.pocket_access_token, settings.archive_tag, settings.items_per_cycle, settings.num_videos, settings.num_images, settings.num_longreads, settings.longreads_wordcount)
    print('\033[0;36m' + dip + '\033[0;m')

  if options.list:
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

  # purge options
  if hasattr(options, 'purge_choice'):

    if options.purge_choice == 'list':
      print('\033[0;36mPurging tags in the list\033[0;m')
      purge = pt.purge_tags('unread', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

    if options.purge_choice == 'archive':
      print('\033[0;36mPurging tags in the archive\033[0;m')
      purge = pt.purge_tags('archive', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

    if options.purge_choice == 'all':
      print('\033[0;36mPurging tags in both the archive and the list\033[0;m')
      purge = pt.purge_tags('all', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
      print(purge)

  if options.refresh:
    print('Refreshing at ' + datetime.now().strftime('%a %d %b %Y %H:%M'))
    refresh = pt.refresh(*refresh_settings)
    print('\033[0;36m' + refresh + '\033[0;m')

  if options.stash:
    stash = pt.stash(consumer_key, settings.pocket_access_token, archive_tag, settings.replace_all_tags, settings.retain_tags, settings.ignore_faves, settings.ignore_tags)
    print('\033[0;36m' + stash + '\033[0;m')

  if options.test:
    result = pt.test(consumer_key, settings.pocket_access_token)
    print(result)