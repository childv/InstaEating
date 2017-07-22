# Flask frontend to display Instagram search post results
# Veronica Child, July 2017
from flask import Flask, render_template, jsonify

app = Flask(__name__)

import instagramSearch

@app.route('/')
def main():
	# Gets top post in form of a dictionary
	top_post = instagramSearch.main()
	print top_post['post']

	# return 'Hello world!'
	return render_template('index.html', image_url=top_post['post']['pic_url'])

if __name__ == '__main__':
	app.run(debug=True)