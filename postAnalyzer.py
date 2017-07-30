# postAnalyzer.py
# A program that contains various tests on parsed Instagram data

# import pandas as pd
import sys
from collections import Counter
import json
import spacy
import re
import pandas as pd

global nlp
global common_tokens # composed of hashtags


# Removes @ and # tags from string
# Inspired by https://www.analyticsvidhya.com/blog/2017/04/natural-language-processing-made-easy-using-spacy-%E2%80%8Bin-python/
# param: dirty_str 	string to be cleaned
def remove_tags(tagged_str):
	#print(dirty_str)
	cleaned_str = re.sub('(@[\w.]+)|(#[\w.]*)', '', dirty_str)
	return cleaned_str

# Checks if token is a stop word, tag, or other form of noise
# param: token 		token from unicode encoded spacy document
# return: Boolean 	if token is noise or not
def isNoise(token):
	# Define noisy part of speech tags
	noisy_pos_tags = ['PROP', 'DET', 'PUNCT', 'CONJ', 'SPACE']
	# Define minimum length of token/word
	min_token_len = 2

	common_tokens = [u'food', u'nyc', u'foodnyc', u'foodie', u'food']
	
	if (token.pos_ in noisy_pos_tags):
		return True
	# Is an unremarkable word
	elif token.string.lower() in common_tokens:
		#print("Token is a common word: " + token.string)
		return True
	# Is an at sign
	elif re.match('@[\w.]*', token.string) is not None:
		#print("Removing at match: " + token.string)
		return True
	# Is a hashtag
	elif re.match('#[\w]*', token.string) is not None:
		#print("Removing hashtag match: " + token.string)
		return True
	# Is stop word
	elif token.is_stop == True:
		return True
	elif len(token.string) < min_token_len:
		return True
	else:
		return False


# Sets string to lowercase string
# param: dirty_str 	dirty token from caption
# return: cleaned string
def clean_str(dirty_str):
	string = dirty_str.lower()
	return string.strip()


# Question: What are the most frequently occuring @ signs?
# param: data_file 	JSON-format file that contains instagram post data
# return:	Counter object of all at signs
def get_frequent_ats(data_file):
	count_ats = Counter()

	with open(data_file, "r") as json_file:
		for line in json_file:
			post_json = json.loads(line)
			count_ats.update(post_json['at_signs'])
	
	return count_ats

# Question: What are the most frequently occurring words?
# Inspired by: https://www.analyticsvidhya.com/blog/2017/04/natural-language-processing-made-easy-using-spacy-%E2%80%8Bin-python/
# Inspired by: https://www.analyticsvidhya.com/blog/2017/01/ultimate-guide-to-understand-implement-natural-language-processing-codes-in-python/
def tokenize_json(data_file):
	tok_captions = [] # list of tokens from captions
	count_all = Counter()

	# Iterate through JSON data
	with open(data_file, "r") as json_file:
		for line in json_file:
		 	post_json = json.loads(line)
		 	# Add to list of dictionaries
		 	#json_data.append(post_json)

		 	# Create doc from caption
		 	doc_caption = nlp(post_json['caption'])
		 	#print doc_caption

		 	# Add
		 	clean_caption = [clean_str(term.string) for term in doc_caption
		 	 if not isNoise(term)]

		 	# Create token list from cleaned caption
		 	terms_all = [term for term in clean_caption]
		 	# Update counter
		 	count_all.update(terms_all)

		# count_all = Counter()
	print(count_all.most_common(5)).encode('utf-8')

	return doc_caption

# Question: What are the most frequently occurring words?
# param: data_file 		file to read data from
# param: freq 			number of words to return
def get_freq_words(data_file, freq):
	tok_captions = [] # list of tokens from captions
	count_all = Counter()

	# Define unremarkable words
	common_tokens = [u'food', u'nyc', u'foodnyc', u'foodie', u'food']

	# Iterate through JSON data
	print("Iterating through JSON data...")
	with open(data_file, "r") as json_file:
		i = 0
		for line in json_file:
		 	post_json = json.loads(line)

		 	# Create doc from caption
		 	doc_caption = nlp(post_json['caption'])

		 	# common_tokens.append([hashtag for hashtag in post_json['hashtags']])

		 	# Add clean tokens to list
		 	clean_caption = [clean_str(term.string) for term in doc_caption
		 	 if not isNoise(term)]

		 	# Update counter
		 	count_all.update(clean_caption)
		 	
		 	# Print progress
		 	sys.stdout.write("Parsing line: {}\r".format(i))
		 	sys.stdout.flush()
		 	i += 1

	# Print result
	print("The " + str(freq) + " most common words are:")
	print(count_all.most_common(freq))

	return clean_caption
 
 # Class holder for all things pandas 
 class pandasAnalyzer():
 	# Question: When a post has likes above the mean, are the number of hashtags above the mean too? (or vice versa)
 	# returns: 	number of posts that have number of likes and hashtags above the mean,
 	#			number of posts that have number of likes and hashtags in different direction
 	def series_test():
 		like_values = []
 		num_hashtags_values = []

 		# Iterate through JSON data
		with open(data_file, "r") as json_file:
			for line in json_file:
				post_json = json.loads(line)
				like_values.append(post_json['likes'])
				num_hashtags_values.append(len(post_json['hashtags']))

		variable1 = pd.Series(like_values) # convert list of likes into pandas series
		variable2 = pd.Series(num_hashtags_values) # convert list of no. of hashtags into pandas series

		both_above = (variable1 > variable1.mean()) & (variable2 > variable2.mean())
		both_below = (variable1 < variable1.mean()) & (variable2 < variable2.mean())

		is_same_direction = both_above | both_below
		num_same_direction = is_same_direction.sum()

		# calulate different direction by taking the difference
		num_different_direction = len(variable1) - num_same_direction

		return (num_same_direction, num_different_direction)

if __name__ == '__main__':
	common_tokens = []
	data_file = "data/raw.json"


	# Process English captions
	print("Preloading NLP...")
	nlp = spacy.load('en') # preload
	print("Preload successful.")

	# analyzer = pandasAnalyzer()


	# Process English captions
	#nlp = spacy.load('en') # preload

	#parsed_data = tokenize_json(data_file)
	#counter_ats = get_frequent_ats(data_file)
	#print(counter_ats.most_common(5))

	holder = get_freq_words(data_file, 5)

	try:
		# Taken from: https://nicschrading.com/project/Intro-to-NLP-with-spaCy/
		# Let's look at the sentences
		sents = []
		# # the "sents" property returns spans
		# # spans have indices into the original string
		# # where each index value represents a token
		# for span in parsed_data.sents:
    		# go from the start to the end of each span, returning each token in the sentence
     		# combine each token using join()
     		# sent = ''.join(parsedData[i].string for i in range(span.start, span.end)).strip()
     		# sents.append(sent)
		# for sentence in sents:
		#     print(sentence)

	except TypeError:
		print("Parsed data is not iterable. Is there a problem with the data?")
		sys.exit(1)


