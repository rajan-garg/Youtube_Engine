# mongo.py

from flask import Flask, redirect, url_for, request, render_template
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mydb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'

mongo = PyMongo(app)

@app.route('/video/<vidID>')
def show(vidID):
	star = mongo.db.mycol
	a = star.find_one({'videoInfo.id':vidID})
	return render_template('index.html', videoid = a)

@app.route('/success/<query>')
def success(query):
	star = mongo.db.mycol
	a = star.find( { '$text': { '$search': query } }, { 'score': {'$meta': "textScore"}}).limit(10)
	return render_template('index.html', name = a , q=query)

@app.route('/index',methods = ['POST', 'GET'])
def login():
	user="hello"
	if request.method=="POST":
		user = request.form['nm']
	return redirect(url_for('success',query = user))




if __name__ == '__main__':
    app.run(debug=True)