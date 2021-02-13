#!/usr/bin/env python3

# pocketsnack - KonMari your Pocket tsundoku from the command line
# Copyright (C) 2018 - 2020 Hugh Rundle

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

# You can contact Hugh on email: hugh [at] hughrundle [dot] net

# ----------------
# Import libraries
# ----------------

from argparse import ArgumentParser
import yaml

# bundled with Python
import os
import pkg_resources
import subprocess

# local modules
from pocketsnack import toolkit as pt

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

    if options.config:
      conf = pt.config()
      print(conf)

    elif options.authorise:
      # Run authorise once first to retrieve a pocket_access_token
      auth = pt.authorise(consumer_key)
      print(auth)

    elif options.dedupe:
      if options.tbr:
        state = "archive"
        tag = S['archive_tag']
      else:
        state = "archive" if options.archive else "all" if options.all else "unread"
        tag = False
      
      location = tag if tag else state if state != 'unread' else 'list'
      print('  \033[46;97mChecking for duplicates in ' + location + '\033[0;m')
      pt.dedupe(state, tag, consumer_key, access_token)

    elif options.lucky_dip:
      print('  \033[46;97mRunning lucky dip...\033[0;m')
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
      print('  \033[46;97m' + dip + '\033[0;m')

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
          print(collection + 'has ' + items + ' items ' + 'updated prior to ' + str(options.before) + ' days ago and ' + str(longreads) + ' are longreads.\033[0;m')
        elif options.since:
          print(collection + 'has ' + items + ' items ' + 'updated since ' + str(options.since) + ' days ago and ' + str(longreads) + ' are longreads.\033[0;m')
        else:
          print(collection + 'has ' + items + ' items and '  + str(longreads) + ' are longreads.\033[0;m')

      if options.archive:
        response = pt.info(consumer_key, access_token, archive_tag, options.before, options.since)
        if len(response) > 0:
          print_info(response, '  \033[46;97mThe TBR archive ')
        else:
          print('  \033[46;97mNo items match that query\033[0;m')

      elif options.list:
        response = pt.info(consumer_key, access_token, False, options.before, options.since)
        if len(response) > 0:
          print_info(response, '  \033[46;97mThe user List ')
        else:
          print('  \033[46;97mNo items match that query\033[0;m')

      else:
        print('\n  \033[46;97m--info\033[0;m requires a second argument (-a or -l). Check \033[46;97mpocketsnack --help\033[0;m for more information\n')

    elif options.purge:

      if options.list:
        print('  \033[46;97mPurging tags in the list\033[0;m')
        purge = pt.purge_tags(
          'unread', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        print(purge)

      elif options.archive:
        print('  \033[46;97mPurging tags in the archive\033[0;m')
        purge = pt.purge_tags(
          'archive',
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        print(purge)

      elif options.all:
        print('  \033[46;97mPurging tags in both the archive and the list\033[0;m')
        purge = pt.purge_tags(
          'all', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        print(purge)

      elif options.tbr:
        print('  \033[46;97mPurging tags in tbr archive\033[0;m')
        purge = pt.purge_tags(
          'tbr', 
          retain_tags, 
          archive_tag, 
          consumer_key, 
          access_token, 
          options.before, 
          options.since
          )
        print(purge)

      else:
        print('\n  \033[46;97m--purge\033[0;m requires a second argument (-a, -l or -b). Check \033[46;97mpocketsnack --help\033[0;m for more information\n')

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
      print('  \033[46;97m' + stash + '\033[0;m')

    elif options.test:
      result = pt.test(consumer_key, access_token)
      print(result)
    
    elif options.version:
      # version number from package info
      vnum = pkg_resources.require("pocketsnack")[0].version
      print(vnum)

    elif set(true_vars).intersection(orphans):
      print('\n   That command cannot be used by itself. Check \033[46;97mpocketsnack --help\033[0;m for more information\n')

    else:
      print('  \033[46;97mpocketsnack\033[0;m requires commands and/or flags to do anything useful. Try \033[46;97mpocketsnack -h\033[0;m for more information')

  except NameError:
    # this happens when there is no config file
    # since we already provide an error message below
    # we do nothing here
    pass

# -----------------------------------
# Parse commands (the action is here)
# -----------------------------------
try:
  config_file = os.path.expanduser('~/.pocketsnack_conf.yml')
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

    parser = ArgumentParser(description='\033[1;36mpocketsnack: KonMari your Pocket tsundoku from the command line.\033[1;m')
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
        "-c", "--config", action="store_true", help="create or edit your config file stored at ~/.pocketsnack_conf.yml"
    )
    actions.add_argument(
        "-d", "--lucky_dip", action="store_true", help="move random items tagged 'tbr' from archive to list, depending on config"
    )
    actions.add_argument(
        "--dedupe", action="store_true", help="de-duplicate list (-l), archive (-a), tbr items (--tbr) or all (-b)- defaults to list"
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

  if __name__ == '__main__':

    main()

except FileNotFoundError:
  print('  \033[46;97mpocketsnack\033[0;m needs a config file!')
  conf = pt.config()
  print(conf)
