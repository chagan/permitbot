"""
Bot to get data from Chicago data portal and tweet it.
"""

#!/usr/bin/env python

import time, urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, twitter, locale, os
import simplejson as json
from datetime import date, datetime, timedelta
from config import config

locale.setlocale( locale.LC_ALL, '' )

# Get text and post it to Twitter
def post_status(text):
	api = twitter.Api(consumer_key=config['consumer_key'],
	            		consumer_secret=config['consumer_secret'],
	                    access_token_key=config['access_token_key'],
	                    access_token_secret=config['access_token_secret'])

	status = api.PostUpdate(text)

# Test connection to twitter api
def test_api():
	api = twitter.Api(consumer_key=config['consumer_key'],
	            		consumer_secret=config['consumer_secret'],
	                    access_token_key=config['access_token_key'],
	                    access_token_secret=config['access_token_secret'])
	
	print(api.VerifyCredentials())
	return api

# Search the dataportal for building permits or the given number of days, limit and offset
# Days controls how far back to look, offset controls how far back in the list to look,
# and limit is max number of results to return. 1000 is most portal allows.
def get_data(limit=1000,offset=0, days=1):

	days = int(days)
	endpoint = 'http://data.cityofchicago.org/resource/ydr8-5enu.json?'

	yesterday = (date.today() - timedelta(days=days)).isoformat()
	#yesterday = date.today().isoformat()
	query = "$where=_issue_date>'%s' &$limit=%s&$offset=%s" % (yesterday, limit, offset)

	qquery = urllib.parse.quote(query, '=&?$')
	url = endpoint+qquery

	try:
		resp = urllib.request.urlopen(url)
		contents = resp.read()
		return contents
	except urllib.error.HTTPError as error:
		print(error.read())
	
# Search for individual permits greater than $500,000 and tweet
# Takes number of days to look back as arguement
def find_high(days=1):
	
	# Retrieve json of permits, parse
	data = get_data(days=days)
	permits = json.loads(data)

	# Go through each permit checking totals
	for permit in permits:
		
		cost = float(permit['_estimated_cost'])
		id = permit['id']
		num = permit['permit_']
		
		suffix = ''
		if '_suffix' in permit:
			suffix = permit['_suffix']

		permit_type = ''
		if '_permit_type' in permit:
			permit_type = "for" + permit['_permit_type'].split('-')[1].lower()

		address = permit['street_number'] + " " + permit['street_direction'] + " " +permit['street_name'].lower().capitalize() + " " + suffix.lower().capitalize()
		permitdate = datetime.strptime(permit['_issue_date'],"%Y-%m-%dT%H:%M:%S")
		prettydate = permitdate.strftime("%b. %d")

		link = "http://chicagocityscape.com/?pid=%s" % num
		
		# Check if permit value is large enough
		if cost > 500000:

			# Check if permit is already in our list
			dupe = duplicate_check(id,'tweeted_permit_ids.txt')
			if dupe == 0:
				text =  "We got a big one: $"+ "{:,.0f}".format(cost) +" permit " + permit_type +" issued on " + prettydate + " at " + address + " " +link
				print(text)
				post_status(text)

				# Once tweeted, add file to list
				add_id_to_file(id,'tweeted_permit_ids.txt')

# Retrieve summary of permits for given number of days
def get_summary(days=30):

	# Retrieve json of permits, parse
	data = get_data(days=days)
	permits = json.loads(data)

	cost = 0
	offset = 0
	link = 'http://chicagocityscape.com/dashboard.php'

	# Loop through permits can get more data until we run out of permits
	while len(permits) > 0:

		for permit in permits:
			cost += float(permit['_estimated_cost'])

		offset += len(permits)
		print(offset)

		# Get more data, incrementing call by offset = number of records already parsed
		data = get_data(days=days,offset=offset)
		permits = json.loads(data)

	text = "Over the past " + str(days) + " days there have been " + "{:,.0f}".format(offset) + " permits issued in Chicago, totaling $" + "{:,.0f}".format(cost) + " " + link

	print(text)
	post_status(text)

# Search for individual demolition permits and tweet
# Takes number of days to look back as arguement
def find_demo(days=1):
	
	# Retrieve json of permits, parse
	data = get_data(days=days)
	permits = json.loads(data)

	# Go through each permit checking type
	for permit in permits:
		
		id = permit['id']
		num = permit['permit_']
		
		suffix = ''
		if '_suffix' in permit:
			suffix = permit['_suffix']

		permit_type = ''
		if '_permit_type' in permit:
			permit_type = permit['_permit_type'].split('-')[1].lower()

		address = permit['street_number'] + " " + permit['street_direction'] + " " +permit['street_name'].lower().capitalize() + " " + suffix.lower().capitalize()
		permitdate = datetime.strptime(permit['_issue_date'],"%Y-%m-%dT%H:%M:%S")
		prettydate = permitdate.strftime("%b. %d")

		link = "http://chicagocityscape.com/?pid=%s" % num
		
		# Check if permit type is demolition
		if permit_type == " wrecking/demolition":

			# Check if permit is already in our list
			dupe = duplicate_check(id,'tweeted_demo_ids.txt')
			if dupe == 0:
				text =  "Building (maybe) coming down: New wrecking/demolition permit at " + address + " issued " + prettydate + " " + link
				print(text)
				post_status(text)

				# Once tweeted, add file to list
				add_id_to_file(id,'tweeted_demo_ids.txt')

# Check mentions and reply if tweet matches pattern
def reply():

	api = twitter.Api(consumer_key=config['consumer_key'],
	            		consumer_secret=config['consumer_secret'],
	                    access_token_key=config['access_token_key'],
	                    access_token_secret=config['access_token_secret'])

	id_file = 'replied_mentions.txt'
	since_id = get_most_recent_id(id_file)

	mentions = api.GetMentions(since_id=since_id)
	
	for tweet in reversed(mentions):
		id = tweet.id_str
		print(id)
		replied = duplicate_check(id,'replied_mentions.txt')

		if replied == 0:
			add_id_to_file(id,id_file)
			if tweet.coordinates:
				print(tweet.coordinates)




# Check if a permit has already been tweeted by comparing against external file of ids
def duplicate_check(id,file):
	if not os.path.isfile(file):
		open(file, 'w+')
		
	found = 0
	with open(file, 'r') as idfile:
		for line in idfile:
			if id in line:
				found = 1
	return found

# Write id to external file
def add_id_to_file(id,file):
	with open(file, 'a') as file:
		file.write(str(id) + "\n")

# Get first id from external file
def get_most_recent_id(file):
	if not os.path.isfile(file):
		open(file, 'w+')

	with open(file, 'r') as file:
		first_id = file.readline().strip()
		return first_id


if __name__ == "__main__":
	reply()