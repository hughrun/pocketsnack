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


if __name__ == '__main__':
  arguments = sys.argv

  if len(arguments) > 1:

    if arguments[1] == 'authorise':
      # Run authorise once first to retrieve a pocket_access_token
      auth = pt.authorise(consumer_key, redirect_uri)
      print(auth)

    elif arguments[1] == "list":
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

    elif arguments[1] == "archive":
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

    elif arguments[1] == 'refresh':
      print('Refreshing at ' + datetime.now().strftime('%a %d %b %Y %H:%M'))
      refresh = pt.refresh(*refresh_settings)
      print('\033[0;36m' + refresh + '\033[0;m')

    elif arguments[1] == 'stash':
      stash = pt.stash(consumer_key, settings.pocket_access_token, archive_tag, settings.replace_all_tags, settings.retain_tags, settings.ignore_faves, settings.ignore_tags)
      print('\033[0;36m' + stash + '\033[0;m')

    elif arguments[1] == 'lucky_dip':
      print('\033[0;36mRunning lucky dip...\033[0;m')
      dip = pt.lucky_dip(consumer_key, settings.pocket_access_token, settings.archive_tag, settings.items_per_cycle, settings.num_videos, settings.num_images, settings.num_longreads, settings.longreads_wordcount)
      print('\033[0;36m' + dip + '\033[0;m')

    elif arguments[1] == 'purge_tags':

      if len(arguments) < 3:
        print('\033[0;36mWhoops, you need to use a second argument with purge_tags.\033[0;m')
        print('\033[0;36mTry "list", "archive" or "all".\033[0;m')

      elif arguments[2] == 'list':
        print('\033[0;36mPurging tags in the list\033[0;m')
        purge = pt.purge_tags('unread', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
        print(purge)

      elif arguments[2] == 'archive':
        print('\033[0;36mPurging tags in the archive\033[0;m')
        purge = pt.purge_tags('archive', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
        print(purge)

      elif arguments[2] == 'all':
        print('\033[0;36mPurging tags in both the archive and the list\033[0;m')
        purge = pt.purge_tags('all', settings.retain_tags, archive_tag, consumer_key, settings.pocket_access_token)
        print(purge)
      else:
        print('\033[0;36mWhoops, you used an unknown argument to purge_tags.\033[0;m')
        print('\033[0;36mPossible options are "purge_tags list", "purge_tags archive" or "purge_tags all".\033[0;m')

    elif arguments[1] == 'test':
      result = pt.test(consumer_key, settings.pocket_access_token)
      print(result)

    else:
      print('That argument is unknown. Check README.md for valid pocketsnack arguments.') # TODO: need to create a man page for this
  else:
    print('Whoops, you forgot to add an "argument". If you have not run anything yet, start with "pocketsnack authorise"')