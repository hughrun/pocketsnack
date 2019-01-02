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
import webbrowser
import json
import urllib

# local modules
import settings

# ----------------
# Create app
# ----------------

# Log in to Pocket in a web browser
# Go to https://getpocket.com/developer and click 'CREATE NEW APP'
# Complete the form: you will need all permissions, and the platform should be 'Desktop (other)'
# Your new app will show a 'consumer key', which you need to paste into the first line in settings.py

# Pocket expects particular HTTP headers to send and receive JSON
headers = {"Content-Type": "application/json; charset=UTF-8", "X-Accept": "application/json"}

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

def choose():
  # choose items to put back into the user List
  pass

def get_list(consumer_key, pocket_access_token):
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

def get_tbr(consumer_key, pocket_access_token, archive_tag):
  # only return items in the archive, tagged with whatever the archive tag is
  params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "state": "archive", "tag": archive_tag}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  return request.json()

def purge_tags():
  # remove all tags from all items 
  # optionally in List only, archive only or both
  # optionally keep certain tags
  pass

def stash(consumer_key, pocket_access_token, archive_tag, fave):
  if fave:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token, "favorite": "0"}
  else:
    params = {"consumer_key": consumer_key, "access_token": pocket_access_token}
  request = requests.post('https://getpocket.com/v3/get', headers=headers, params=params)
  list_items = request.json()

  # replace all tags with just the archive tag/s
  actions = []
  item_list = list_items['list']
  for item in item_list:
    item_id = item_list[item]['item_id']
    action = {"action": "tags_replace", "item_id": item_id, "tags": archive_tag}
    actions.append(action)

  actions_string = json.dumps(actions)
  # now URL encode it using urllib
  actions_escaped = urllib.parse.quote(actions_string)
  # POST
  requests.post('https://getpocket.com/v3/send?actions=' + actions_escaped + '&access_token=' + pocket_access_token + '&consumer_key=' + consumer_key)
  return 'done'