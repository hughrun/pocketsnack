# pocket-toolkit - a collection of functions to manage your Pocket account

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
import fileinput
import json
import random
import re
import socket
import time
import urllib
import webbrowser

# local modules
import settings

# request functions (make this a proper class object later)
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

# process tag updates
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
      print('\033[0;32mOk\033[0;m')
    else:
      print('\031[0;41mOh dear, something went wrong.\033[0;m')
    time.sleep(2) # don't fire off requests too quickly

# ----------------
# Create app
# ----------------

# Log in to Pocket in a web browser
# Go to https://getpocket.com/developer and click 'CREATE NEW APP'
# Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
# Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

# ----------------
# Authorise
# ----------------

def authorise(consumer_key, redirect_uri): # With an 's'. Deal with it.
  paramsOne = {"consumer_key": consumer_key, "redirect_uri": redirect_uri}
  # set up step 1 request - this should return a 'code' aka 'request token'
  requestOne = requests.post('https://getpocket.com/v3/oauth/request', headers=headers, params=paramsOne)
  # get the JSON response and save the token to a param for the next step
  request_token = requestOne.json()['code']
  # print the request token to the console so you know it happened
  print('Your request token (code) is ' + request_token)

  # now you need to authorise the app in your Pocket account
  # build the url
  auth_url = 'https://getpocket.com/auth/authorize?request_token=' + request_token + '&redirect_uri=' + redirect_uri
  # open the authorisation page in a new tab of your default web browser
  webbrowser.open(auth_url, new=2)

  # We're not writing a server app here so we use a little hack to check whether the user has finished authorising before we continue
  # Just wait for the user (you!) to indicate they have finished authorising the app
  # the '\n' prints a new line
  print('Authorise your app in the browser tab that just opened.')
  user_input = input('Type "done" when you have finished authorising the app in Pocket \n>>')

  if user_input == "done":
    # now we can continue
    # do a new request, this time to the oauth/authorize endpoint with the same JSON headers, but also sending the code as a param
    paramsTwo = {"consumer_key": consumer_key, "code": request_token}
    requestTwo = requests.post('https://getpocket.com/v3/oauth/authorize', headers=headers, params=paramsTwo)
    # get the JSON response as a Python dictionary and call it 'res'.
    res = requestTwo.json()
    # Finally we have the access token!
    print('Access token for ' + res['username'] + ' is ' + res['access_token'])
    # Assign the access token to a parameter called access_token
    access_token = res['access_token']
    # replace the pocket_access_token line rather than just adding an extra at the end
    settings_file = fileinput.FileInput("settings.py", inplace=True)
    repl = "pocket_access_token = " + "'" + access_token + "'"
    for line in settings_file:
      line = re.sub('(pocket_access_token)+.*', repl, line)
      print(line.rstrip())
    return 'Token added to settings.py - you are ready to use pocketsnack.'

# this is used in main.py
def get_list(consumer_key, pocket_access_token):
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

# this is used in main.py
def get_tbr(consumer_key, pocket_access_token, archive_tag):
  # only return items in the archive, tagged with whatever the archive tag is
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "tag": archive_tag}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

# choose items to put back into the user List
def lucky_dip(consumer_key, pocket_access_token, archive_tag, items_per_cycle, num_videos, num_images, num_longreads, longreads_wordcount):

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
      request = get(params)
      tbr = request.json()['list']

      # before we go any further, make sure there actually is something in the TBR list!
      if len(tbr) > 0:
        available = len(tbr) # set this value here before it gets changed
        # just to make it clearer, and create a copy
        items_needed = items_per_cycle

        # we'll use this to report what was added
        chosen = {}
        #####################
        # filtering formats
        #####################
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

        #####################
        # filtering longreads
        #####################
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
        completed_message = 'Success! ' + str(tot_added) + ' items added to your reading list, including '
        if random_choice:
          completed_message += str(chosen['random']) + ' random articles, '
        if tot_images:
          completed_message += str(tot_images) + ' images, '
        if tot_videos:
          completed_message += str(tot_videos) + ' videos, '
        if not random_choice:
          completed_message += str(chosen['longreads']) + ' long reads and ' + str(chosen['shortreads']) + ' short reads, '
        # add this to the end regardless
        completed_message += 'with ' + str(remaining) + ' other items remaining to be read.'
        return completed_message
      # else if there's nothing tagged with the archive_tag
      else:
        return 'Nothing to be read!'
    else:
      if attempts < 4:
        attempts += 1
        time.sleep(10)
        print('Attempting to connect...')
        return run_lucky_dip(attempts)
      else:
        msg = "Sorry, no connection after 4 attempts."
        return msg

  return run_lucky_dip(0)

def purge_tags(state, retain_tags, archive_tag, consumer_key, pocket_access_token):

  params = {
    "consumer_key": consumer_key, 
    "access_token": pocket_access_token, 
    "state": state, 
    "detailType": "complete"
    }

  # check we're online
  if connection_live() == True:
    # GET the list
    request = get(params).json()['list']
    actions = []

    for item in request:
      # find the item tags
      item_tags = []
      if 'tags' in request[item]:
        for tag in request[item]['tags']:
          item_tags.append(tag)
      # keep any retain_tags like we use in stash
      if len(item_tags) > 0:
        update = {"item_id": item, "action": "tags_replace"} # item is the ID because it's the dict key
        retain_tags.add(archive_tag) # we don't want to wipe out the archive tag on archived items!
        update["tags"] = list(retain_tags.intersection(item_tags))
        actions.append(update)
      # otherwise just clear all tags
      else:
        update = {"item_id": item, "action": "tags_clear"} # item is the ID because it's the dict key
        actions.append(update)

    process_items(actions, consumer_key, pocket_access_token)
    return '\033[0;36mUndesirable elements have been purged.\033[0;m' 

def refresh(consumer_key, pocket_access_token, archive_tag, replace_all_tags, retain_tags, favorite, ignore_tags, items_per_cycle, num_videos, num_images, num_longreads, longreads_wordcount):
  # this is the job that should run regularly
  # run stash
  print('Stashing...')
  stash_msg = stash(consumer_key, pocket_access_token, archive_tag, replace_all_tags, retain_tags, favorite, ignore_tags)
  print(stash_msg)
  if stash_msg != 'Sorry, no connection after 4 attempts.':
    # run lucky_dip
    print('Running lucky dip...')
    ld_message = lucky_dip(consumer_key, pocket_access_token, archive_tag, items_per_cycle, num_videos, num_images, num_longreads, longreads_wordcount)
    return ld_message
  else:
    return 'Refresh aborted.'

"""
Stash

stash(consumer_key, pocket_access_token, archive_tag [, retain_tags] [, favorite])

Stash applies the archive_tag to all items in the User List, then archives everything in the List.

Options:

retain_tags - a list of tags that should not be removed from items when adding the archive_tag. If you don't want to retain any tags, this value should be False. Defaults to False
favorite - boolean indicating whether to ignore (i.e. leave in the user list) favorite items. Defaults to True

"""

def stash(consumer_key, pocket_access_token, archive_tag, replace_all_tags, retain_tags, favorite, ignore_tags):
  # if ignore_faves is set to True, don't get favorite items
  if favorite:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "detailType": "complete", "state": "unread", "favorite": "0"}
    print('Skipping favorited items...')
  else:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "detailType": "complete", "state": "unread"}

  def run_stash(attempts):
      if connection_live() == True:
        # GET the list
        request = get(params)
        list_items = request.json()
        actions = []
        item_list = list_items['list']
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

        print('archiving ' + str(len(archive_actions)) + ' items...' )
        
         # archive items
        process_items(archive_actions, consumer_key, pocket_access_token)

        # return a list of what was stashed and, if relevant, what wasn't
        skipped_items = len(item_list) - len(items_to_stash)
        return str(len(items_to_stash)) + ' items archived with "' + archive_tag + '" and ' + str(skipped_items) + ' items skipped due to retain tag.'
      else:
        if attempts < 4:
          attempts += 1
          time.sleep(10)
          print('Attempting to connect...')
          return run_stash(attempts)
        else:
          msg = "Sorry, no connection after 4 attempts."
          return msg

  return run_stash(0)

def test(consumer_key, pocket_access_token):

  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "count": "1", "detailType": "complete"}

  # GET the list
  request = get(params)
  list_items = request.json()

  return json.dumps(list_items, indent=4, default=str)