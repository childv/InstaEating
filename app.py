# Flask frontend to display Instagram search post results
# Veronica Child, July 2017
from flask import Flask, render_template, jsonify

app = Flask(__name__)

import instagramSearch

top_post = instagramSearch.main()

@app.route('/')
def main():
	# return 'Hello world!'
	return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)