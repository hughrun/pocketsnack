pocket_consumer_key = ''
pocket_redirect_uri = 'https://hugh.li/success'
items_per_cycle = 10
archive_tag = 'TBR' # apply this tag before archiving items
ignore_tag = 'keep' # don't archive items with this tag
replace_all_tags = False # if set to True this will replace ALL tags on an item in the user's List with the archive_tag and anything in exclude_tags. If set to False, the archive tag is still added but any existing tags are retained.
exclude_tags = ['GLAM Blog Club', 'aus glam blogs', 'empocketer'] # if replace_all_tags is set to True, you can still retain particular tags by adding them to the exclude_tags list
minimum_videos = None # if you change this to an integer this many items_per_cycle will be videos (if there are any videos in your list)
minimum_images = None # if you change this to an integer this many items_per_cycle will be images (if there are any images in your list)
# ensure the last line is blank so that authorisation token is stored correctly
