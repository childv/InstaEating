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
class pandasAnalyzer:
 	def __init__(self):
 		pass
 	# Question: When a post has one variable above the mean, is the other variable above the mean too? (or vice versa)
 	# returns: 	number of posts that have number of likes and hashtags above the mean,
 	#			number of posts that have number of likes and hashtags in different direction
 	def series_test(self, var1, var2):
 		var1_values = []
 		var2_values = []

 		# Iterate through JSON data
		with open(data_file, "r") as json_file:
			for line in json_file:
				post_json = json.loads(line)
				var1_values.append(post_json[var1])
				var2_values.append(len(post_json[var2]))

		# convert list in pandas series
		var1_series = pd.Series(var1_values)
		var2_series = pd.Series(var2_values)

		both_above = (var1_series > var1_series.mean()) & (var2_series > var2_series.mean())
		both_below = (var1_series < var1_series.mean()) & (var2_series < var2_series.mean())

		is_same_dir = both_above | both_below
		num_same_dir = is_same_dir.sum()

		# calulate different direction by taking the difference
		num_different_dir = len(var1_series) - num_same_dir

		print("For post " + var1 + " and " + var2 + ":")	
		print("Same direction: " + str(num_same_dir) + " --- Diff direction: " + str(num_different_dir))

		return (num_same_dir, num_different_dir)

if __name__ == '__main__':
	data_file = "data/raw.json"

	analyzer = pandasAnalyzer()
	num1, num2 = analyzer.series_test('likes', 'hashtags')


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


