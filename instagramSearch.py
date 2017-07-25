# instagram-search.py
# A program that grabs the most common posts on restaurants
# Veronica Child
# July 10, 2017

# Code that scrapes Instagram's explore page to get the latest posts regarding food
# Inspired by Tom Dickinson's tutorial, http://tomkdickinson.co.uk/2016/12/extracting-instagram-data-part-1/

import sys
import requests
import json
import re
import csv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class DBHandler():
	def __init__(self):
		self.client = MongoClient()
		# Attempt to connect to MongoDB
		try:
			# The ismaster command does not require auth
			self.client.admin.command('ismaster')
		except ConnectionFailure:
			print("Server not available. Exiting...")
			sys.exit(1)

	# Save posts
	def get_posts(self, insert_object):
		db = self.client['posts']

		# Return all documents in latst_posts collection
		cursor = db.latest_posts.find()
		# Return documents with likes greater than 100
		#cursor = db.latest_posts.find({"likes": {"$gt": 100}})
		# Return document with specific _id
		#cursor = db.latest_posts.find_one({"_id" : insert_object.inserted_id})

		# iterate cursor and print matching docs
		i = 0
		for document in cursor:
			print("Doc number: " + str(i))
			# get hex encoded version of ObjectId
			print("Doc id: " + str(document['_id']))
			#print(document)
			i += 1

		if (i == 0):
			print("No documents retrieved")

	# Saves posts using MongoDB
	# param: posts	list of InstagramPosts
	def save_posts(self, posts):
		# create a connection - if unspecififed, runs on localhost port 27017
		client = MongoClient();
		# access database named posts
		db = client['posts']

		# convert list of posts into a dictionary format
		post_list = []
		for post in posts:
			post_list.append(post.to_dict())
		posts_dict = {'posts': post_list}

		# insert a document into collection named latest_posts
		# result is an InsertOneResult object
		insert_object = db.latest_posts.insert_one(posts_dict)
		# get unique id to insert object
		# WHAT IS THE DIFFERENCE BETWEEN INSERTONERESULT AND DOC _ID??
		print("Unique id:")
		print(insert_object.inserted_id)
		return insert_object


# Post Model
class InstagramPost:
	def __init__(self, caption, likes, user_id, pic_url, date):
		self.caption = caption
		self.likes = likes
		self.user_id = user_id
		self.at_signs = self.parse_at_signs(caption)
		self.hashtags = self.parse_hashtags(caption)
		self.pic_url = pic_url
		self.date = date

	def get_caption(self):
		return self.caption

	def get_likes(self):
		return self.likes

	def get_user_id(self):
		return self.user_id

	def get_at_signs(self):
		return self.at_signs

	def get_pic_url(self):
		return self.pic_url

	def get_hashtags(self):
		return self.hashtags

	# Returns list of associated at sign '@' in a string
	# OPTIMIZE: remove double mentions
	def parse_at_signs(self, string):
		results = []
		# Matches anything after an at sign '@'
		# @		anything that begins with @
		# \w 	matches any unicode character at least one time
		at_compiler = re.compile('@[\w.]+')
		results = at_compiler.findall(string)
		return results

	# Returns list of associated hashtags '#' in a string
	# Can't have spaces or special characters
	def parse_hashtags(self, string):
		results = []
		# Matches anything after a hashtag '#'
		# '#'	anything that begins with #
		# \w 	matches any unicode character at least one tim
		hashtag_compiler = re.compile('#[\w.]+')
		results = hashtag_compiler.findall(string)
		return results

	def to_dict(self):
		return {
			'caption': self.caption,
			'likes': self.likes,
			'user_id': self.user_id,
			'at_signs': self.at_signs,
			'pic_url': self.pic_url,
			'hashtags' : self.hashtags,
			'date': self.date
		}

class InstagramExploreSearch:
	'''
	Class that mines the instagram explore page with a given hashtag.
	'''
	
	def __init__(self, hashtag):
		self.hashtag = hashtag
		self.root_url = 'https://www.instagram.com'
		self.all_mined_posts = []

	# Returns list of Instagram posts given hashtag search params
	def extract_posts(self):
		'''
		Extracts Instagram posts with the given hashtag
		:param tag: Hashtag to extract
		'''
		url_search = self.root_url + '/explore/tags/%s/' % self.hashtag
		page = requests.get(url_search).text
		soup = BeautifulSoup(page, 'html.parser')
		# print(soup.prettify())
		potential_query_ids = self.get_query_ids(soup)

		# Find post data
		for script_tag in soup.find_all('script'):
			if script_tag.text.startswith('window._sharedData ='):
				# Clean data for JSON loading
				json_data = script_tag.text.replace('window._sharedData = ', '')
				json_data = re.sub(';$', '', json_data)		# replace last ';'
				json_data = json.loads(json_data)
				break

		# TEST: print recent JSON data
		# print json.dumps(json_data, indent=4)
		posts = []

		# Check if next page is available
		print('Checking if next page is available...')
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		if (media['page_info']['has_next_page'] == True):
			print('Page available. Extracting query IDs...')
			# Figure out valid queryID
			# Inspired by https://github.com/tomkdickinson/Instagram-Search-API-Python/blob/master/instagram_search.py
			end_cursor = media['page_info']['end_cursor']	# use to query next page
			success = False

			# call go to new page
			# test query ids from response page for correct one
			# each id is its own image??
			for potential_query_id in potential_query_ids:
				# URL build based on a potential query id of a post
				query_url = self.root_url + "/graphql/query/?query_id=%s&tag_name=%s&first=10&after=%s" % (
					potential_query_id, self.hashtag, end_cursor)
				
				# Check if query id is valid
				try:
					query_data = requests.get(query_url).json()
					if 'hashtag' not in query_data['data']:
						# Empty response?
						continue
					query_id = potential_query_id
					success = True
					break

				except ValueError as ve:
					# no valid JSON returned, continue in loop
					pass

			# Exit if no valid queries
			if not success:
				log.error("Extracted query ids were not valid")
				sys.exit(1)
			print("Successfully extracted query ids.")
			
			i = 0

			# write to local csv
			# with open('data/raw.csv', 'wb') as csvfile:
			# 	keys = ['caption', 'likes', 'user_id', 'at_signs', 'hashtags', 'pic_url', 'date']
			# 	w = csv.DictWriter(csvfile, fieldnames=keys)
			# 	w.writeheader()
			# 	#w = csv.writer(csvfile, delimiter='\t')
			# 	#w.writerow(keys)

			# write to local JSON
			with open('data/raw.json', 'w') as json_file:
				print('Begin Instagram mining...')
				while end_cursor is not None:
					# URL build based on confirmed query id of a post
					query_url = self.root_url + "/graphql/query/?query_id=%s&tag_name=%s&first=10&after=%s" % (
						query_id, self.hashtag, end_cursor)
					query_data = json.loads(requests.get(query_url).text)
					end_cursor = query_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

					# TEST: print recent queried JSON data
					# print json.dumps(query_data, indent=4)

					# Collect posts after 'Load More' button
					for node in query_data['data']['hashtag']['edge_hashtag_to_media']['edges']:
						extracted_post = self.extract_recent_query_post(node['node'])
						posts.append(extracted_post)

						## Write post data to local csv
						# w.writerow(extracted_post.to_dict())

						## Write post data to local JSON
						#json_post = json.loads(extracted_post.to_dict())
						#json.dump(extracted_post.to_dict(), json_file)
						json_file.write("{}\n".format(json.dumps(data)))
						
						# Hard-coded loop cut off
						print("Loop: " + str(i))
						i += 1
						if (i > 20000):
							end_cursor = None
							# quit at 16210 before
							#return posts
				
				# Save posts to MongoDB	
				# insert_object = self.db.save_posts(posts)

				# self.db.get_posts(insert_object)

		# Determine what posts to return
		#posts = self.extract_recent_posts(json_data)
		return []

	# Collect recent posts from initial root explore page
	# param: node 	JSON umbrella key for recent post data
	def extract_recent_post(self, node):
		user_id = int(node['owner']['id'])
		likes = int(node['likes']['count'])
		pic_url = node['display_src']
		date = node['date']
		# If no caption present, then caption is an empty string
		if 'caption' in node:
			caption = node['caption']
		else:
			caption = ""
		post = InstagramPost(caption, likes, user_id, pic_url, date)
		
		return post

	# Collect recent posts beyond 'Load More' query button
	# param: node 	JSON umbrella key for queried recent post data
	def extract_recent_query_post(self, node):
		# print(json.dumps(node, indent=4))
		
		user_id = int(node['owner']['id'])
		likes = int(node['edge_liked_by']['count'])
		pic_url = node['display_url']
		date = node['taken_at_timestamp']

		# If no caption present, then caption is an empty string
		caption = ""
		if 'edge_media_to_caption' in node:
			# !! COULD BE MORE CAPTION??
			for section in node['edge_media_to_caption']['edges']:
				caption += section['node']['text'].encode('utf-8')
			#caption = node['edge_media_to_caption']['edges'][0]['node']['text']

		post = InstagramPost(caption, likes, user_id, pic_url, date)
		return post

	# Collect top posts
	def get_top_posts(self, json_data):
		top_posts = json_data['entry_data']['TagPage'][0]['tag']['top_posts']

		posts = []
		# Iterate and collect top posts
		for node in top_posts['nodes']:
			post = self.extract_recent_post(node)
			posts.append(post)

		return posts

	# Collect recent posts from initial Instagram Explore page
	# param: json_data 	JSON data taken from initial page
	def extract_recent_posts(self, json_data):
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		posts = []

		for node in media['nodes']:
			post = self.extract_recent_post(node)
			posts.append(post)
			# Optimize: add nodes such that they are in order, else sort

			# print json.dumps(node, indent=4)

			# write to local csv


		return posts


	# Collect query ids from JS when load page button is clicked
	# Taken from https://github.com/tomkdickinson/Instagram-Search-API-Python/blob/master/instagram_search.py
	def get_query_ids(self, doc):
		query_ids = []
		# Scrape HTML by iterating through script tags
		for script in doc.find_all("script"):
			# Example of find:
			# <script crossorigin="anonymous" src="/static/bundles/en_US_Commons.js/69787846f22e.js" type="text/javascript">
			if script.has_attr("src") and "en_US_Commons" in script['src']:
				# Build url when load more button is clicked
				text = requests.get("%s%s" % (self.root_url, script['src'])).text

				# Write response to text file for analysis
				text_file = open("page_output.txt", "w")
				text_file.write(text.encode('utf8'))
				text_file.close()

				# Iterate to find all query ids
				for query_id in re.findall("(?<=queryId:\")[0-9]{17,17}", text):
					query_ids.append(query_id)
		return query_ids


# Runs search with given hashtag. Returns top post in form of a dictionary
def main():
	search_results = InstagramExploreSearch('foodnyc').extract_posts()

	# Exit if no posts - would result in AttributeError otherwise
	if (len(search_results) == 0):
		print("No posts found. Exiting...")
		sys.exit()

	most_likes = 0
	top_post = None

	for post in search_results:
		if post.get_likes() > most_likes:
			most_likes = post.get_likes()
			top_post = post

	print("Caption: " + top_post.get_caption() + "\nLikes: " + str(top_post.get_likes()))
	print("At signs: ")
	for sign in top_post.get_at_signs():
		print(sign + ', ')
	print("Picture url: " + top_post.get_pic_url())

	# get data of top post in dict format
	return top_post.to_dict()



if __name__ == '__main__':
	main()



