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

class InstagramPost:
	def __init__(self, caption, likes, user_id):
		self.caption = caption
		self.likes = likes
		self.user_id = user_id

	def get_caption(self):
		return self.caption

	def get_likes(self):
		return self.likes

	def get_user_id(self):
		return self.user_id

	# Returns list of associated hashtags with caption
	def parse_hashtags(self):
		return


class InstagramExploreSearch:
	'''
	Class that mines the instagram explore page with a given hashtag.
	'''
	
	def __init__(self, hashtag):
		self.hashtag = hashtag

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

		media = json_data['entry_data']['TagPage'][0]['tag']['media']
		posts = []

		# Iterate and collect recent posts
		for node in media['nodes']:
			user_id = int(node['owner']['id'])
			likes = int(node['likes']['count'])
			caption = node['caption']
			post = InstagramPost(caption, likes, user_id)
			posts.append(post)
			# Optimize: add nodes such that they are in order, else sort

			# print json.dumps(node, indent=4)

		# print(posts[0].get_caption())
		print url_search
		return posts


	def save_results(self, post_results):
		pass

if __name__ == '__main__':
	search_results = InstagramExploreSearch('foodnyc').extract_posts()
	
	most_likes = 0
	top_post = None

	for post in search_results:
		if post.get_likes() > most_likes:
			most_likes = post.get_likes()
			top_post = post

	print("Caption: " + top_post.get_caption() + "\nLikes: " + str(top_post.get_likes()))



