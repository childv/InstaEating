# Flask frontend to display Instagram search post results
# Veronica Child, July 2017
from flask import Flask, render_template, jsonify

app = Flask(__name__)

import instagramSearch

top_post = instagram-search

@app.route('/')
def main():
	return render_template('/template/index.html')

if __name__ == '__main__':
	app.run()