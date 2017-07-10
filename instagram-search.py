# instagram-search.py
# A program that grabs the most common posts on restaurants
# Veronica Child
# July 10, 2017

# Code that scrapes Instagram's explore page to get the latest posts regarding food
# Inspired by Tom Dickinson's tutorial, http://tomkdickinson.co.uk/2016/12/extracting-instagram-data-part-1/

import requests
import json
from bs4 import BeautifulSoup

class InstagramExploreSearch(hashtag):
	"""
	Class that mines the instagram explore page with a given hashtag.
	"""
	root_url = "https://www.instagram.com/explore/tags/"
	
	def __init__(self):
		super().__init__()

	def extract_posts(self, tag):
		"""
		Extracts Instagram posts with the given hashtag
		:param tag: Hashtag to extract
		"""
		url_search = root_url + tag
		page = requests.get(url_search).text
		soup = BeautifulSoup(page, "html.parser")

	def save_results(self, post_results):
		pass

if __name__ == '__main__':
	InstagramExploreSearch().extract_posts("food")


