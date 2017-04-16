# mongo.py

from flask import Flask, redirect, url_for, request, render_template
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
from py2neo import Graph, authenticate


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mydb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'

authenticate("localhost:7474", "neo4j", "ronalpha")
graph = Graph();

mongo = PyMongo(app)

@app.route('/video/<vidID>')
def show(vidID):
	star = mongo.db.mycol
	a = star.find_one({'videoInfo.id':vidID})
	b=graph.run("match(n:Youtube)-[r:`SAME_CHANNEL`]-(n2) where n.name= {n} return n2 limit 10",n = vidID)
	out=[]
	for i in b:
		out.append(star.find_one({'videoInfo.id':i['n2']['name']}))

	return render_template('index.html',name=out , videoid = a)

@app.route('/success/<query>')
def success(query):
	star = mongo.db.mycol
	a = star.find( { '$text': { '$search': query } }, { 'score': {'$meta': "textScore"}}).limit(10)
	return render_template('index.html', name = a)

@app.route('/index',methods = ['POST', 'GET'])
def login():
	user="hello"
	if request.method=="POST":
		user = request.form['nm']
	return redirect(url_for('success',query = user))




if __name__ == '__main__':
    app.run(debug=True)