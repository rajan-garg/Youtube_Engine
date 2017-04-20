# import the Flask class from the flask module
from flask import Flask, session, render_template, redirect, url_for, request,  Response
from flaskext.mysql import MySQL
from flask_session import Session
import MySQLdb
from flask_pymongo import PyMongo
import json
from py2neo import Graph, authenticate

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mydb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydb'

authenticate("localhost:7474", "neo4j", "ronalpha")
graph = Graph();

mongo = PyMongo(app)


mysql = MySQL()

acc= ''

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'ronalpha'
app.config['MYSQL_DATABASE_DB'] = 'youtube'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/video/<vidID>')
def video(vidID):
	star = mongo.db.mycol
	a = star.find_one({'videoInfo.id':vidID})
	b=graph.run("match(n:Youtube)-[r]-(n2) where n.name= {n} return n2 order by r.weight desc limit 10",n = vidID)
	out=[]
	global acc
	if acc!='':
		cursor = mysql.connect().cursor()
		cursor.execute('SELECT * FROM vids WHERE user="' + acc + '" AND videoid="' + vidID + '";')
		data = cursor.fetchone()
		conn=MySQLdb.connect(host="localhost", user="root", passwd="ronalpha", db="youtube")
		cursor=conn.cursor()
		print data
		print "Yolo"
		if data:
			print data[1]
			c = int(data[2]) + 1
			print c
			query2 = 'UPDATE vids SET count="' + str(c) + '"' + 'WHERE user="' + acc + '" AND ' + 'videoid="' + vidID + '"'
			cursor.execute(query2)
			conn.commit()
			cursor.close()
			conn.close()
		else:
			query = 'INSERT INTO vids(user,videoid,count) VALUES (' + ' "' + acc + '" ,"'+ vidID + '",' + str(1) + ')'
			cursor.execute(query)
			conn.commit()
			cursor.close()
			conn.close()

	for i in b:
		out.append(star.find_one({'videoInfo.id':i['n2']['name']}))

	if acc=='':
		return render_template('index.html',name=out , videoid = a)
	else:
		return render_template('welcome.html',username=acc,name=out , videoid = a)

@app.route('/clicks')
def clicks():
	global acc
	print acc
	if acc!='':
		print "yoloyool"
		cursor = mysql.connect().cursor()
		cursor.execute('SELECT * FROM vids WHERE user="' + acc + '" ORDER BY time DESC;')
		data = cursor.fetchall()
		print data[0][1]
		out=[]
		star = mongo.db.mycol
		for i in data:
			out.append(star.find_one({'videoInfo.id':i[1]}))
		return render_template('welcome.html',username=acc,name=out)
	return Response("Please login")


@app.route('/fav')
def fav():
	global acc
	print acc
	if acc!='':
		print "yoloyool"
		cursor = mysql.connect().cursor()
		cursor.execute('SELECT * FROM vids WHERE user="' + acc + '" AND count>=2 ORDER BY count DESC;')
		data = cursor.fetchall()
		print data[0][1]
		out=[]
		star = mongo.db.mycol
		for i in data:
			out.append(star.find_one({'videoInfo.id':i[1]}))
		return render_template('welcome.html',username=acc,name=out)
	return Response("Please login")

@app.route('/trend')
def rec():
	global acc
	star = mongo.db.mycol
	a = star.find().sort("videoInfo.statistics.viewCount",-1).limit(11)
	if acc=='':
		return render_template('index.html',name = a)
	else:
		return render_template('welcome.html',username=acc,name = a)


@app.route('/success/<query>')
def success(query):
	global acc
	print acc
	print query
	star = mongo.db.mycol
	a = star.find( { '$text': { '$search': query } }, { 'score': {'$meta': "textScore"}}).sort([('score',{'$meta':'textScore'})]).limit(11)
	if acc=='':
		return render_template('index.html',name = a)
	else:
		return render_template('welcome.html',username=acc,name = a)

@app.route('/search',methods = ['POST', 'GET'])
def search():
	user="hello"
	if request.method=="POST":
		user = request.form['nm']
	global acc
	#if acc=='':
	return redirect(url_for('success',query = user))
	#else:
	#	return redirect(url_for('welcome'))


@app.route('/home')
def home():
	
	if 'username' in session:
		global acc
		username = session['username']
		acc = username
		print acc
		return redirect(url_for('welcome'))
	else:
		return render_template('index.html')

@app.route('/welcome')
def welcome():
	global acc
	#return acc
	return  render_template('welcome.html',username=acc)


@app.route('/auth', methods=['GET', 'POST'])
def auth():
	if request.method == 'POST':
		u = request.form['username']
		p = request.form['password']

	global acc
	acc = u

	session['username'] = u

	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * FROM credentials WHERE userid='" + u + "' AND pass='" + p + "';")
	data = cursor.fetchone()
	if data is None:
		return render_template('index.html')
	else:
		return redirect(url_for('welcome'))

@app.route('/register', methods=['GET', 'POST'])
def reg():
	if request.method == 'POST':
		u = request.form['username']
		p = request.form['password']

	conn=MySQLdb.connect(host="localhost", user="root", passwd="ronalpha", db="youtube")
	cursor=conn.cursor()

	global acc
	acc=u

	session['username'] = u
	query = "INSERT INTO credentials(userid,pass) VALUES (%s,%s)"
	args = (u,p)

	cursor.execute(query,args)

	conn.commit()
	cursor.close()
	conn.close()
	return redirect(url_for('welcome'))

@app.route('/logout')
def logout():
	global acc
	acc= ''

	session.pop('username', None)
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.secret_key = 'qwerty'
	app.run(debug=True)
