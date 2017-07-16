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

	# Returns list of associated hashtags '#' in a string
	# Can't have spaces or special characters
	def parse_hashtags(self, caption):
		return

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

	# Returns list of Instagram posts given hashtag search params
	def extract_posts(self):
		'''
		Extracts Instagram posts with the given hashtag
		:param tag: Hashtag to extract
		'''
		url_search = 'https://www.instagram.com/explore/tags/%s/' % self.hashtag
		page = requests.get(url_search).text
		soup = BeautifulSoup(page, 'html.parser')

		# Find post data
		for script_tag in soup.find_all('script'):
			if script_tag.text.startswith('window._sharedData ='):
				# Clean data for JSON loading
				json_data = script_tag.text.replace('window._sharedData = ', '')
				json_data = re.sub(';$', '', json_data)		# replace last ';'
				json_data = json.loads(json_data)
				break

		#print json.dumps(json_data, indent=4)

		# Check if next page is available
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		if (media['page_info']['has_next_page'] == True):
			pass

		# Determine what posts to return
		posts = self.get_top_posts(json_data)
		return posts


	def save_results(self, post_results):
		pass

	def node_to_post(self, node):
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

	# Collect top posts
	def get_top_posts(self, json_data):
		top_posts = json_data['entry_data']['TagPage'][0]['tag']['top_posts']
		posts = []

		# Iterate adn collect top posts
		for node in top_posts['nodes']:
			post = self.node_to_post(node)
			posts.append(post)

		return posts

	# Collect recent posts
	def get_recent_posts(self, json_data):
		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		posts = []

		for node in media['nodes']:
			post = self.node_to_post(node)
			posts.append(post)
			# Optimize: add nodes such that they are in order, else sort

			# print json.dumps(node, indent=4)

		return posts



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


