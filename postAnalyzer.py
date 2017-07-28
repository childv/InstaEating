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
# caption_data = ( item['value'] for item in test_data )


# Cleans string of @ and # tags
# param: dirty_str 	string to be cleaned
def remove_tags(dirty_str):
	#print(dirty_str)
	cleaned_str = re.sub('(@[\w.]+)|(#[\w.]*)', '', dirty_str)
	return cleaned_str

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
def tokenize_json(data_file):
	tok_captions = [] # list of tokens from captions
	count_all = Counter()

	# Iterate through JSON data
	with open(data_file, "r") as json_file:
		for line in json_file:
		 	post_json = json.loads(line)
		 	# Add to list of dictionaries
		 	#json_data.append(post_json)

		 	# Create doc from cleaned caption (no @ or #)
		 	clean_caption = remove_tags(post_json['caption'])
		 	doc_caption = nlp(clean_caption)
		 	#print doc_caption

		 	# Create list from cleaned caption
		 	terms_all = [term for term in clean_caption]
		 	# Update counter
		 	count_all.update(terms_all)

		 	# Iterate through tokens in caption
		 	# for token in doc_caption:
		 	# 	tok_captions.append(token)
		 	# 	#print token
		 	# 	pass

	print(count_all.most_common(5))

	return doc_caption
 
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
	data_file = "data/raw.json"

	analyzer = pandasAnalyzer()


	# Process English captions
	#nlp = spacy.load('en') # preload

	#parsed_data = tokenize_json(data_file)
	#counter_ats = get_frequent_ats(data_file)
	#print(parsed_ats.most_common(5))

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


