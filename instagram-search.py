# instagram-search.py
# A program that grabs the most common posts on restaurants
# Veronica Child
# July 10, 2017

# Code that scrapes Instagram's explore page to get the latest posts regarding food
# Inspired by Tom Dickinson's tutorial, http://tomkdickinson.co.uk/2016/12/extracting-instagram-data-part-1/

import requests
import json
import re
from bs4 import BeautifulSoup

# Post Model
class InstagramPost:
	def __init__(self, caption, likes, user_id, at_signs, pic_url):
		self.caption = caption
		self.likes = likes
		self.user_id = user_id
		self.at_signs = at_signs
		self.pic_url = pic_url

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

class InstagramPostParser:
	def __init__(self):
		# Matches anything after an at sign '@'
		# @		anything that begins with @
		# \w 	matches any unicode character at least one time
		self.at_compiler = re.compile('@[\w.]+')
		# Matches anything after a hashtag '#'
		self.hashtag_compiler = re.compile('#[\w.]+')

	# Returns list of associated hashtags '#' in a string
	# Can't have spaces or special characters
	def parse_hashtags(self, caption):
		results = []
		results = self.hashtag_compiler.finall(string)
		return results

	# Returns list of associated at sign '@' in a string
	def parse_at_signs(self, string):
		results = []
		results = self.at_compiler.findall(string)
		return results

class InstagramExploreSearch:
	'''
	Class that mines the instagram explore page with a given hashtag.
	'''
	
	def __init__(self, hashtag):
		self.hashtag = hashtag
		self.parser = InstagramPostParser()
		self.root_url = 'https://www.instagram.com'

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

		#print json.dumps(json_data, indent=4)

		posts = []
		# Check if next page is available
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		if (media['page_info']['has_next_page'] == True):
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
				
				# Chekf if query id is valid
				try:
					query_data = requests.get(url).json()
					if 'hashtag' not in query_data['data']:
						# Empty response?
						continue
					query_id = potential_query_id
					success = True
					break

				except JSONDecodeError as de:
					# no valid JSON returned, continue in loop
					pass

			# Exit if no valid queries
			if not success:
				log.error("Extracted query ids were not valid")
				sys.exit(1)
			
			while end_cursor is not None:
				# URL build based on confirmed query id of a post
				query_url = self.root_url + "/graphql/query/?query_id=%s&tag_name=%s&first=10&after=%s" % (
					query_id, self.hashtag, end_cursor)
				query_data = json.loads(requests.get(url).text)
				end_cursor = data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

				# Collect posts after 'Load More' button
				for node in data['data']['hashtag']['edge_hashtag_to_media']['edges']:
					posts.append(self.extract_receent_query_post(node['node']))
				self.save_posts(posts)


		# Determine what posts to return
		posts = self.get_top_posts(json_data)
		return posts


	# Saves posts
	def save_posts(self, post_results):
		pass

	def extract_recent_post(self, node):
		user_id = int(node['owner']['id'])
		likes = int(node['likes']['count'])

		# If no caption present, then caption is an empty string
		if 'caption' in node:
			caption = node['caption']
			at_signs = self.parser.parse_at_signs(caption)
		else:
			caption = ""
			at_signs = ""

		pic_url = node['display_src']

		post = InstagramPost(caption, likes, user_id, at_signs, pic_url)
		
		return post

	def extract_recent_query_post(self, node):
		user_id = int(node['id'])
		likes = int(node['likes']['count'])

		# If no caption present, then caption is an empty string
		if 'caption' in node:
			caption = node['edge_media_to_caption']['edges'][0]['node']['text']
			at_signs = self.parser.parse_at_signs(caption)
		else:
			caption = ""
			at_signs = ""

		pic_url = node['display_url']

		post = InstagramPost(caption, likes, user_id, at_signs, pic_url)
		
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

	# Collect recent posts
	def get_recent_posts(self, json_data):
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		posts = []

		for node in media['nodes']:
			post = self.extract_recent_post(node)
			posts.append(post)
			# Optimize: add nodes such that they are in order, else sort

			# print json.dumps(node, indent=4)

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



if __name__ == '__main__':
	search_results = InstagramExploreSearch('foodnyc').extract_posts()
	
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


