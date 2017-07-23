# Flask frontend to display Instagram search post results
# Veronica Child, July 2017
from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

import instagramSearch

@app.route('/', methods=['GET', 'POST'])
def main():
	# Gets top post in form of a dictionary
	top_post = instagramSearch.main()
	#print("At signs 2: " + top_post['post']['at_signs'][0])

	# convert dict to JSON - how to use?
	top_post_json = jsonify(top_post)

	# return 'Hello world!'
	return render_template('index.html',
		image_url=top_post['pic_url'],
		caption=top_post['caption'],
		likes=top_post['likes'],
		result=top_post)

if __name__ == '__main__':
	app.run(debug=True)