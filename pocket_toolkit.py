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
import json
import random
import urllib
import webbrowser

# local modules
import settings


# request functions (make this a proper class object later)

# Pocket expects particular HTTP headers to send and receive JSON
headers = {"Content-Type": "application/json; charset=UTF-8", "X-Accept": "application/json"}

def get(params):
  return requests.post('https://getpocket.com/v3/get', headers=headers, params=params)

def send(actions_escaped, consumer_key, pocket_access_token):
  # POST changes to tags
  requests.post('https://getpocket.com/v3/send?actions=' + actions_escaped + '&access_token=' + pocket_access_token + '&consumer_key=' + consumer_key)
  return 'done'

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
    with open("settings.py", "a") as settings_file:
      settings_file.write("pocket_access_token = " + "'" + access_token + "'\n")

def get_list(consumer_key, pocket_access_token):
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

def get_tbr(consumer_key, pocket_access_token, archive_tag):
  # only return items in the archive, tagged with whatever the archive tag is
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "tag": archive_tag}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

# choose items to put back into the user List
def lucky_dip(consumer_key, pocket_access_token, archive_tag, items_per_cycle, minimum_videos, minimum_images, num_longreads, longreads_wordcount):
  
  # get everything with the archive_tag
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "tag": archive_tag}
  request = get(params)
  tbr = request.json()['list']

  # get a random selection
  selection = random.sample(list(tbr), items_per_cycle)
  
  # Now un-archive everything in the selection
  actions = []
  
  for item in selection:
    # item_id = item_list[item]['item_id']
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

def purge_tags():
  # remove all tags from all items 
  # optionally in List only, archive only or both
  # optionally keep certain tags
  pass

"""
Stash

stash(consumer_key, pocket_access_token, archive_tag [, retain_tags] [, favorite])

Stash applies the archive_tag to all items in the User List, then archives everything in the List.

Options:

retain_tags - a list of tags that should not be removed from items when adding the archive_tag. If you don't want to retain any tags, this value should be False. Defaults to False
favorite - boolean indicating whether to ignore (i.e. leave in the user list) favorite items. Defaults to True

"""

def stash(consumer_key, pocket_access_token, archive_tag, replace_all_tags, retain_tags, favorite):
  if favorite:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "favorite": "0"}
  else:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token}
  
  # GET the list
  request = get(params)
  list_items = request.json()

  # FIXME: temporarily make replace_all_tags False until retain_tags functionality works
  replace_all_tags = False

  actions = []
  item_list = list_items['list']
  for item in item_list:
    item_id = item_list[item]['item_id']
    # set up the action dict
    action = {"item_id": item_id}
    if replace_all_tags: # temporarily always False until the functionality below can work
      action["action"] = "tags_replace"
      # are we retaining any tags?
      if retain_tags: # retain_tags should either be False or a list
        # we need to check whether this item actually contains any of the retain_tags
        # FIXME: this won't work because Pocket doesn't actually return "tags", despite the API documentation
        # TODO: maybe we process these first? i.e. use GET tag_name for each retain_tag, tag them with the archive_tag and then archive? But even then we don't know whether they contain multiple tags to keep.
        tags_to_keep = set(retain_tags).intersection(item_list[item]['tags'])
        action["tags"] = tags_to_keep
      else:
        action["tags"] = archive_tag
    else: # just add the archive tag
      action["action"] = "tags_add"
      action["tags"] = archive_tag
    # action is now completed, add it to the list     
    actions.append(action)

  actions_string = json.dumps(actions)
  # now URL encode it using urllib
  actions_escaped = urllib.parse.quote(actions_string)
  # post update to tags
  send(actions_escaped, consumer_key, pocket_access_token)

  # Now archive everything
  archive_actions = []
  
  for item in item_list:
    item_id = item_list[item]['item_id']
    item_action = {"item_id": item_id, "action": "archive"}
    archive_actions.append(item_action)

  # stringify
  archive_items_string = json.dumps(archive_actions)
  archive_escaped = urllib.parse.quote(archive_items_string)

  # archive items
  return send(archive_escaped, consumer_key, pocket_access_token)