# pocket-toolkit - a collection of functions to manage your Pocket account

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

# You can contact Hugh on Mastodon at @hugh@ausglam.space
# or Twitter at @hughrundle
# or email hugh [at] hughrundle [dot] net

# ----------------
# Import libraries
# ----------------

import requests

# bundled with Python
from datetime import datetime, time, timedelta
import fileinput
import json
import os
import random
import re
import socket
import subprocess
import sys
import time
import urllib
import webbrowser

# global for config
config_file = os.path.expanduser('~/.pocketsnack_conf.yml')

# ----------------
# Create app
# ----------------

# Log in to Pocket in a web browser
# Go to https://getpocket.com/developer and click 'CREATE NEW APP'
# Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
# Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

# -----------------
# reusable functions
# -----------------

# Pocket expects particular HTTP headers to send and receive JSON
headers = {"Content-Type": "application/json; charset=UTF-8", "X-Accept": "application/json"}

# send GET requests
def get(params):
  return requests.post('https://getpocket.com/v3/get', headers=headers, params=params)

# send POST requests
def send(actions_escaped, consumer_key, pocket_access_token):
  # POST changes to tags
  return requests.post('https://getpocket.com/v3/send?actions=' + actions_escaped + '&access_token=' + pocket_access_token + '&consumer_key=' + consumer_key)
# check the internet connection is live
def connection_live():
  try:
    socket.create_connection(("getpocket.com", 443), 10)
    return True
  except OSError:
      pass
  return False

# make a unix timestamp for before/after flags with Pocket's 'since' param
def get_timestamp(since):
  now = datetime.now()
  delta = timedelta(days=since) 
  since_time = datetime.strftime(now - delta, '%c')
  strptime = time.strptime(since_time)
  return time.mktime(strptime) # return Unix timestamp

def get_item_list(params, before, since):
  if before:
    all_items = get(params)
    params['since'] = get_timestamp(before)
    since_items = get(params)
    # get non-intersection of 2 groups to get only items last changed 'before'
    item_list = all_items.json()['list'] # everything
    since_list = since_items.json()['list'] # only things since 'before'
    if len(since_list) > 0:
      for key in since_list.keys():
        item_list.pop(key, None) # remove everything from items_list that is in since_list
    return item_list
  elif since:
    timestamp = get_timestamp(since)
    params['since'] = timestamp
    return get(params).json()['list']
  else:
    return get(params).json()['list']

# --------------------
# process tag updates
# --------------------

def process_items(actions, consumer_key, pocket_access_token):
  # Update the tags
  # group into smaller chunks of 20 to avoid a 414 (URL too long) error
  tag_chunks = [actions[i:i+20] for i in range(0, len(actions), 20)]

  # process each chunk
  for i, chunk in enumerate(tag_chunks):

    actions_string = json.dumps(chunk)
    # now URL encode it using urllib
    actions_escaped = urllib.parse.quote(actions_string)
    print('   Processing ' + str(i*20) + ' to ' + str((i*20)+len(tag_chunks[i])) + ' of ' + str(len(actions)) + '...', end="", flush=True) # printing like this means the return callback is appended to the line
    # post update to tags
    update = send(actions_escaped, consumer_key, pocket_access_token)
    if update.raise_for_status() == None:
      print('\033[0;32mOk\033[0;m') # Print 'Ok' in green.
    else:
      print('\031[0;41mOh dear, something went wrong.\033[0;m') # Print error in red
    time.sleep(2) # don't fire off requests too quickly

# ----------------
# Configuration
# ----------------

def config():

  try:
    with open(config_file, 'x') as new_config:
      new_config.write('pocket_consumer_key: YOUR_KEY_HERE\n')
      new_config.write('items_per_cycle: 10\n')
      new_config.write('archive_tag: tbr\n')
      new_config.write('ignore_tags: \n')
      new_config.write('  - ignore\n')
      new_config.write('ignore_faves: true\n')
      new_config.write('replace_all_tags: false\n')
      new_config.write('retain_tags:\n')
      new_config.write('  - glam blog club\n')
      new_config.write('  - empocketer\n')
      new_config.write('  - important dog stories\n')
      new_config.write('longreads_wordcount: 3000\n')
      new_config.write('num_videos: null\n')
      new_config.write('num_images: null\n')
      new_config.write('num_longreads: 2\n')
      new_config.write('pocket_access_token: null')
      new_config.close()

      if sys.platform == 'win32' or sys.platform == 'cygwin':
        win_path = os.path.normpath(config_file)
        os.startfile(win_path) # windows path
      if sys.platform == 'darwin':
        subprocess.call(["open", config_file])
      else:
        subprocess.call(["xdg-open", config_file])
      
      return '  Config file created. Use \033[46;97mpocketsnack --auth\033[0;m to complete your setup.'
  
  except Exception:

    if sys.platform == 'win32' or sys.platform == 'cygwin':
      win_path = os.path.normpath(config_file)
      os.startfile(win_path) # windows path
    if sys.platform == 'darwin':
      subprocess.call(["open", config_file])
    else:
      subprocess.call(["xdg-open", config_file])
    
    return 'Config file opened for editing.'

# ----------------
# Authorise
# ----------------

def authorise(consumer_key): # With an 's'. Deal with it.
  redirect_uri = 'https://hugh.run/success'
  paramsOne = {"consumer_key": consumer_key, "redirect_uri": redirect_uri}
  # set up step 1 request - this should return a 'code' aka 'request token'
  requestOne = requests.post('https://getpocket.com/v3/oauth/request', headers=headers, params=paramsOne)
  # get the JSON response and save the token to a param for the next step
  request_token = requestOne.json()['code']
  # print the request token to the console so you know it happened
  print('\033[0;36m  Your request token (code) is \033[0;m' + request_token)

  # now you need to authorise the app in your Pocket account
  # build the url
  auth_url = 'https://getpocket.com/auth/authorize?request_token=' + request_token + '&redirect_uri=' + redirect_uri
  # open the authorisation page in a new tab of your default web browser
  webbrowser.open(auth_url, new=2)

  # We're not writing a server app here so we use a little hack to check whether the user has finished authorising before we continue
  # Just wait for the user (you!) to indicate they have finished authorising the app
  # the '\n' prints a new line
  print('\033[0;36m  Authorise your app in the browser tab that just opened.\033[0;m')
  user_input = input('Type "done" when you have finished authorising the app in Pocket \n>>')

  if user_input == "done":
    # now we can continue
    # do a new request, this time to the oauth/authorize endpoint with the same JSON headers, but also sending the code as a param
    paramsTwo = {"consumer_key": consumer_key, "code": request_token}
    requestTwo = requests.post('https://getpocket.com/v3/oauth/authorize', headers=headers, params=paramsTwo)
    # get the JSON response as a Python dictionary and call it 'res'.
    res = requestTwo.json()
    # Finally we have the access token!
    print('\033[0;36m  Access token for ' + res['username'] + ' is \033[0;m' + res['access_token'])
    # Assign the access token to a parameter called access_token
    access_token = res['access_token']
    # replace the pocket_access_token line rather than just adding an extra at the end
    settings_file = fileinput.FileInput(config_file, inplace=True)
    repl = "pocket_access_token: " + access_token
    for line in settings_file:
      line = re.sub('(pocket_access_token)+.*', repl, line)
      print(line.rstrip())
    return '\033[0;36m  Token added to config file - you are ready to use pocketsnack!\033[0;m 🎉'

# ------------------------------
# Read info about Pocket account
# ------------------------------

def info(consumer_key, pocket_access_token, archive_tag, before, since):

  params = {
    "consumer_key": consumer_key, 
    "access_token": pocket_access_token, 
    }
  if archive_tag:
    # state is archive & use archive tag
    params['state'] = 'archive'
    params['tag'] = archive_tag
  else:
    # state is unread
    params['state'] = 'unread'

  items =  get_item_list(params, before, since)
  return items

# -----------------------------------
# lucky dip from archive back to list
# -----------------------------------

def lucky_dip(consumer_key, pocket_access_token, archive_tag, items_per_cycle, num_videos, num_images, num_longreads, longreads_wordcount, before, since):

  def run_lucky_dip(attempts):
    if connection_live() == True:
      # This function is called below to un-archive everything in the selection
      def readd(selection):
        actions = []
        for item in selection:
          item_readd = {"item_id": item, "action": "readd"}
          actions.append(item_readd)
          # remove archive_tag as well, otherwise the item will keep appearing after it's read and archived by the user
          item_detag = {"item_id": item, "action": "tags_remove", "tags": archive_tag}
          actions.append(item_detag)
        # stringify
        items_string = json.dumps(actions)
        escaped = urllib.parse.quote(items_string)
        # re-add items
        return send(escaped, consumer_key, pocket_access_token)

      # get everything in the archive with the archive_tag
      params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "tag": archive_tag}

      tbr = get_item_list(params, before, since)

      # before we go any further, make sure there actually is something in the TBR list!
      if len(tbr) > 0:
        available = len(tbr) # set this value here before it gets changed
        # just to make it clearer, and create a copy
        items_needed = items_per_cycle

        # we'll use this to report what was added
        chosen = {}

        # filtering formats
        # -----------------
        videos = []
        images = []

        for item in tbr:
          if num_videos and 'has_video' in tbr[item]:
            if tbr[item]['has_video'] == '2':
              # it's a video
              videos.append(item)
          if num_images and 'has_image' in tbr[item]:
            if tbr[item]['has_image'] == '2':
              # it's an image
              images.append(item)

        if num_videos:
          # don't select more than the total items_needed
          required_videos = items_needed if items_needed <= num_videos else num_videos
          selected_videos = videos if len(videos) <= required_videos else random.sample(videos, required_videos)
          # re-add the videos
          if len(selected_videos) > 0:
            readd(selected_videos)
            # adjust the total items we need to look for
            items_needed -= len(selected_videos)
          chosen['videos'] = len(selected_videos)

        if num_images:
          required_images = num_images if num_images <= items_needed else items_needed
          selected_images = images if len(images) <= required_images else random.sample(images, required_images)
          if len(selected_images) > 0:
            readd(selected_images)
            # adjust the total items we need to look for
            items_needed -= len(selected_images)
          chosen['images'] = len(selected_images)

        # filtering longreads
        # -------------------
        if num_longreads:
          long_reads = []
          for item in tbr:
            # is it a long read?
            if 'word_count' in tbr[item]:
              words = int(tbr[item]['word_count'])
              if words > longreads_wordcount:
                long_reads.append(item) # we only need to append the item_id

          total_longreads = len(long_reads)
          total_shortreads = len(tbr) - total_longreads
          required_shortreads = items_needed - num_longreads
          enough_longreads = total_longreads >= num_longreads
          enough_shortreads = total_shortreads >= required_shortreads

          # if there are enough longreads AND enough shortreads, go ahead
          if enough_longreads and enough_shortreads:
            # select random longreads
            # note we need to check whether any are actually required at this point, otherwise we run the risk of items_needed becoming a negative number
            selected_longreads = (random.sample(long_reads, num_longreads)) if items_needed > 0 else []
            # add random shortreads
            # first we need to remove the longreads from tbr:
            for article in long_reads:
              tbr.pop(article, None)
            # now grab a random selection to fill our items_needed quota
            selected_shortreads = random.sample(list(tbr), required_shortreads) if required_shortreads > 0 else []
            # add the two lists together
            selection = selected_longreads + selected_shortreads
            chosen['longreads'] = len(selected_longreads)
            chosen['shortreads'] = len(selected_shortreads)
            readd(selection)
          # If there are too few longreads but enough shortreads, take what LR we have and make up the difference
          elif enough_shortreads:
            # select all of the longreads
            selected_longreads = long_reads
            # add random shortreads
            # first we need to remove the longreads from tbr:
            for article in long_reads:
              tbr.pop(article, None)
            # now grab a random selection to fill our items_needed quota
            difference = items_needed - len(selected_longreads)
            # make sure you have enough of the new total
            enough_difference = difference <= total_shortreads
            if enough_difference:
              selected_shortreads = random.sample(list(tbr), difference) if difference > 0 else []
            # if there are too few longreads AND too few shortreads just grab what shortreads you have
            else:
              selected_shortreads = list(tbr) # note this is the new tbr after we popped the longreads
            # add the two lists together
            selection = selected_longreads + selected_shortreads
            chosen['longreads'] = len(selected_longreads)
            chosen['shortreads'] = len(selected_shortreads)
            readd(selection)
          # if there are enough longreads but too few shortreads, use all the shortreads and make up the difference with longreads
          elif enough_longreads:
            # add all the shortreads there are
            # first we need to remove the longreads from tbr:
            for article in long_reads:
              tbr.pop(article, None)
            # the new tbr is now entirely shortreads
            selected_shortreads = list(tbr)
            # now grab a random selection of long reads to fill our items_needed quota
            difference = items_needed - len(selected_shortreads)
            # make sure you have enough of the new total
            enough_difference = difference <= total_longreads
            if enough_difference:
              selected_longreads = random.sample(long_reads, difference) if difference > 0 else []
            # if there are too few longreads AND too few shortreads just grab what longreads you have
            else:
              selected_longreads = long_reads
            # add the two lists together
            selection = selected_longreads + selected_shortreads
            chosen['longreads'] = len(selected_longreads)
            chosen['shortreads'] = len(selected_shortreads)
            readd(selection)
          else:
            # if we get to here there aren't enough of either, so we should just return everything
            chosen['longreads'] = total_longreads
            chosen['shortreads'] = total_shortreads
            readd(list(tbr))
        else: # if num_longreads is False or 0 (which are the same thing)
          # check how many items in total there are in the TBR list
          # if there are fewer than items_needed, just return all of them, otherwise get a random selection
          if items_needed > 0:
            selection = list(tbr) if len(tbr) < items_needed else random.sample(list(tbr), items_needed)
            chosen['random'] = len(selection)
            readd(selection)
      # return a total of what was moved into the list (faves, format etc)
        tot_videos = chosen['videos'] if 'videos' in chosen else None
        tot_images = chosen['images'] if 'images' in chosen else None
        random_choice = 'random' in chosen
        tot_added = 0
        for v in chosen.values():
          tot_added += v
        remaining = available - tot_added
        completed_message = '\033[46;97mSuccess!\033[0;m ' + str(tot_added) + ' items added to your reading list, including '
        if random_choice:
          completed_message += str(chosen['random']) + ' random articles, '
        if tot_images:
          completed_message += str(tot_images) + ' images, '
        if tot_videos:
          completed_message += str(tot_videos) + ' videos, '
        if not random_choice:
          completed_message += str(chosen['longreads']) + ' long reads and ' + str(chosen['shortreads']) + ' short reads, '
        # add this to the end regardless
        caveat = ''
        if before:
          caveat = 'last updated earlier than ' + str(before) + ' days ago '
        if since:
          caveat = 'last updated more recently than ' + str(since) + ' days ago '
        completed_message += 'with ' + str(remaining) + ' other items ' + caveat + 'remaining to be read.'
        return completed_message
      # else if there's nothing tagged with the archive_tag
      else:
        return '  \033[46;97mNothing to be read!\033[0;m'
    else:
      if attempts < 4:
        attempts += 1
        time.sleep(10)
        print('  \033[46;97mAttempting to connect...\033[0;m')
        return run_lucky_dip(attempts)
      else:
        msg = "  \033[46;97mSorry, no connection after 4 attempts.\033[0;m"
        return msg

  return run_lucky_dip(0)

# -----------------
#  purge tags
# -----------------

def purge_tags(state, retain_tags, archive_tag, consumer_key, pocket_access_token, before, since):

  params = {
    "consumer_key": consumer_key, 
    "access_token": pocket_access_token, 
    "state": state, 
    "detailType": "complete"
    }

  if state == "tbr":
    params['state'] = 'archive'
    params['tag'] = archive_tag

  # check we're online
  if connection_live() == True:
    # GET the list
    request = get_item_list(params, before, since)
    actions = []

    if len(request) > 0:
      for item in request:
        item_tags = []
        # find the item tags
        if 'tags' in request[item]:
          for tag in request[item]['tags']:
            item_tags.append(tag)
        # keep any retain_tags like we use in stash
        retain_tags.add(archive_tag) # we don't want to wipe out the archive tag on archived items!
        update = {"item_id": item} 
        intersect = list(retain_tags.intersection(item_tags))
        if len(intersect) > 0:
          update['action'] = 'tags_replace' # item is the ID because it's the dict key
          update["tags"] = intersect # update tags to keep the retain_tags
        # otherwise just clear all tags
        else:
          update['action'] = 'tags_clear' # item is the ID because it's the dict key
        actions.append(update)
      
      process_items(actions, consumer_key, pocket_access_token)
      return '\033[1;36m  Undesirable elements have been purged.\033[1;m' 
    
    else:
      return '\033[0;36m  No items from which to purge tags.\033[0;m'

"""
Stash

stash(consumer_key, pocket_access_token, archive_tag [, retain_tags] [, favorite])

Stash applies the archive_tag to all items in the User List, then archives everything in the List.

Options:

  retain_tags - a list of tags that should not be removed from items when adding the archive_tag. 
  If you don't want to retain any tags, this value should be False. 
  Defaults to False

  favorite - boolean indicating whether to ignore (i.e. leave in the user list) favorite items  
  Defaults to True

"""

# -----------------
# stash items
# -----------------

def stash(consumer_key, pocket_access_token, archive_tag, replace_all_tags, retain_tags, favorite, ignore_tags, before, since):
  print('  \033[46;97mStashing items...\033[0;m')
  # if ignore_faves is set to True, don't get favorite items
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "detailType": "complete", "state": "unread"}
  if favorite:
    params['favorite'] = "0"
    print('  Skipping favorited items...')

  def run_stash(attempts):
    if connection_live() == True:
      # GET the list
      item_list = get_item_list(params, before, since)
      # we store all the 'actions' in an array, then send one big HTTP request to the Pocket API
      actions = []
      # copy items_list so we can alter the copy whilst iterating through the original
      items_to_stash = dict(item_list)
      for item in item_list:
        item_tags = []
        if 'tags' in item_list[item]:
          for tag in item_list[item]['tags']:
            item_tags.append(tag)

        # filter out any items with the ignore tags before dealing with the rest
        if len(ignore_tags) > 0 and len(ignore_tags.intersection(item_tags)) > 0:
            # pop it out of the items_to_stash
            items_to_stash.pop(item, None)
        # Now we process all the tags first, before we archive everything
        elif replace_all_tags:
          # set up the action dict
          action = {"item_id": item, "action": "tags_replace"} # item is the ID because it's the dict key
          # are we retaining any tags?
          if retain_tags: # retain_tags should either be False or a Set
            # find the common tags between retain_tags and item_tags
            # to do this we need retain_tags to be a set, but you can't JSON serialise a set, so we need to turn the result into a list afterwards
            tags_to_keep = list(retain_tags.intersection(item_tags))
            # don't forget to add the archive_tag!
            tags_to_keep.append(archive_tag)
            action["tags"] = tags_to_keep
          # Anything that is still in the user list can be presumed to not have been read
          # when they read it they will archive it (without the archive_tag because lucky_dip removes it)
          else:
            action["tags"] = archive_tag
          actions.append(action)
        else: # if replace_all_tags is False, just add the archive tag without removing any tags
          action = {"item_id": item, "action": "tags_add"} # add new tag rather than replacing all of them
          action["tags"] = archive_tag
          actions.append(action)

      # Update the tags
      process_items(actions, consumer_key, pocket_access_token)

      # Now archive everything
      archive_actions = []

      for item in items_to_stash:
        item_action = {"item_id": item, "action": "archive"}
        archive_actions.append(item_action)

      print('  \033[46;97mArchiving ' + str(len(archive_actions)) + ' items...\033[0;m')

        # archive items
      process_items(archive_actions, consumer_key, pocket_access_token)

      # return a list of what was stashed and, if relevant, what wasn't
      skipped_items = len(item_list) - len(items_to_stash)
      return '  ' + str(len(items_to_stash)) + ' items archived with "' + archive_tag + '" and ' + str(skipped_items) + ' items skipped due to retain tag.'
    else:
      if attempts < 4:
        attempts += 1
        time.sleep(10)
        print('  \033[46;97mAttempting to connect...\033[0;m')
        return run_stash(attempts)
      else:
        msg = "  \033[46;97mSorry, no connection after 4 attempts.\033[0;m"
        return msg

  return run_stash(0)

# -----------------
# test
# -----------------

def test(consumer_key, pocket_access_token):

  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "count": "1", "detailType": "complete"}

  # GET the list
  request = get(params)
  list_items = request.json()

  return json.dumps(list_items, indent=4, default=str)

# -----------------
# de-duplicate
# -----------------

def dedupe(state, tag, consumer_key, pocket_access_token):

  # Retrieving items
  # ----------------
  # retrieve all 'unread' items (i.e. not archived)
  # we use the Retrieve API call = https://getpocket.com/developer/docs/v3/retrieve
  # The endpoint for retrieving is 'get': https://getpocket.com/v3/get
  # detailType should be 'simple' because we don't need any information except for the item_id and the resolved_url
  parameters = {
    "consumer_key" : consumer_key, 
    "access_token" : pocket_access_token, 
    "detailType" : "simple",
    "state" : state
    }

  if tag:
    parameters['tag'] = tag  # if tag exists, add it to parameters

  unread = get(parameters)
  # our items will be under the JSON object's "list" key
  item_list = unread.json()['list']
  
  # make a new dictionary called 'summary'
  # we will use this to look for duplicates
  summary = {}  

  # and make a list called 'items_to_delete'
  items_to_delete = []

  # loop over each key (not the whole object) in item_list
  # 'item' here refers to each item's key, not the whole object/dictionary
  print('  \033[46;97mchecking ' + str(len(item_list)) + ' items...\033[0;m')
  for item in item_list:
    # conveniently the key Pocket uses is the item_id!
    item_id = item

    # we need the item_id from this request so we can use it in the next API call to delete it
    # get the URL by pulling out the value from the dict using the key
    # generally we want to use the 'resolved url' but sometimes that might not exist
    # if so, use the 'given url' instead
    if not 'resolved_url' in item_list[item]:
      # item_list is a Python dictionary where each value is itself another dictionary
      # or in JSON terms, it's an object where each value is another object
      # below we are getting the value of the current item id (i.e the first dict), then checking if there is a value within the second dict for the key 'given_url'
      item_url = item_list[item]['given_url']
    else:  
      item_url = item_list[item]['resolved_url']
    
    # check whether the resolved_url is already in 'summary'
    # if it isn't, make a new entry with resolved_url as the key and a list holding item_id as the value - basically we're reversing the logic of 'item_list'. This will allow us to check for duplicates easily in a moment.
    if not item_url in summary:
      summary[item_url] = [item_id]
    # if it is there already, add the item_id into the existing list
    else:
      summary[item_url].append(item_id)

  # ------------------
  # Finding duplicates
  # ------------------

  # now we look for duplicates (this is why we use the url as the key)
  for item in summary:
    
    # if the length of the list is more than 1, then by definition there must be a duplicate
    if len(summary[item]) > 1:
      print('  \033[46;97m' + item + '\033[0;m occurs ' + str(len(summary[item])) + ' times')
      # keep only the most recently added item by slicing the list to make a new list of everything except the last one (which will be the *first* one that was found)
      duplicates = summary[item][:-1]
      # add each duplicate in the duplicates list for this url to the items_to_delete list
      for item in duplicates:
        items_to_delete.append(item)

  # Deleting duplicates
  # -------------------

  # now use the modify API call to delete duplicate items
  # Docs - https://getpocket.com/developer/docs/v3/modify

  # With our list of duplicate item ids, we create one final list of a bunch of JSON objects
  actions = []

  # for each item to be deleted, append a dictionary to the actions list
  for item_id in items_to_delete:
    actions.append({"action":"delete", "item_id": item_id})

  # Double check you really want to delete them
  if len(actions) > 0:
    print('  \033[107;95mAbout to delete ' + str(len(actions)) + ' duplicate items.\033[0;m')
    print('  \033[107;95mDelete these items? Type "delete" to confirm.\033[0;m')
    check = input('>>')
    if check == 'delete':
      # first turn the list and its component dictionaries into a JSON string
      actions_string = json.dumps(actions)
      # now URL encode it using urllib
      actions_escaped = urllib.parse.quote(actions_string)
      # now POST to pocket and assign the response to a parameter at the same time.
      deleted = send(actions_escaped, consumer_key, pocket_access_token)
      # provide feedback on what happened
      # 'deleted' is a raw http response (it should return '<Response [200]>') 
      # so we need to turn it into a Python string before we can do a comparison
      if str(deleted) == '<Response [200]>':
        print('  \033[46;97m🚮 These duplicates have been deleted:\033[0;m')
        for item in actions:
          print('  \033[46;97m' + item['item_id'] + '\033[0;m')
        # that's it!
      else:
        print('  \033[46;97mSomething went wrong 😟\033[0;m')
    else:
      print('  \033[46;97m✋ deletion cancelled\033[0;m')
  else:
    print('  🎉 \033[46;97mNo duplicates found!\033[0;m')