# postAnalyzer.py
# A program that contains various tests on parsed Instagram data

# import pandas as pd
import sys
from collections import Counter
import json
import spacy
import re

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


		 	#parsed_captions.append(parsed_caption)
		 	#parsed_captions += parsed_caption
		 	#tokens_all =

		# count_all = Counter()
	print(count_all.most_common(5))

	return doc_caption
 

if __name__ == '__main__':
	# Process English captions
	nlp = spacy.load('en') # preload
	data_file = "data/raw.json"


	#parsed_data = tokenize_json(data_file)
	counter_ats = get_frequent_ats(data_file)
	print(parsed_ats.most_common(5))

	try:
		# Let's look at the sentences
		sents = []
		# # the "sents" property returns spans
		# # spans have indices into the original string
		# # where each index value represents a token
		# for span in parsed_data.sents:
  #   		# go from the start to the end of each span, returning each token in the sentence
  #   		# combine each token using join()
  #   			sent = ''.join(parsedData[i].string for i in range(span.start, span.end)).strip()
  #   		sents.append(sent)

		# for sentence in sents:
		#     print(sentence)

	except TypeError:
		print("Parsed data is not iterable. Is there a problem with the data?")
		sys.exit(1)

		# Let's look at the tokens
		# All you have to do is iterate through the parsedData
		# Each token is an object with lots of different properties
		# A property with an underscore at the end returns the string representation
		# while a property without the underscore returns an index (int) into spaCy's vocabulary
		# The probability estimate is based on counts from a 3 billion word
		# corpus, smoothed using the Simple Good-Turing method.
		# for i, token in enumerate(parsed_data):
		#     # print("original:", token.orth, token.orth_)
		#     # print("lowercased:", token.lower, token.lower_)
		#     # print("lemma:", token.lemma, token.lemma_)
		#     # print("shape:", token.shape, token.shape_)
		#     # print("prefix:", token.prefix, token.prefix_)
		#     # print("suffix:", token.suffix, token.suffix_)
		#     # print("log probability:", token.prob)
		#     # print("Brown cluster id:", token.cluster)
		#     # print("----------------------------------------")
		#     if i > 1:
		#     	break

