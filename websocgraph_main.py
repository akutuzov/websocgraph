#!/bin/python
# coding: utf-8
from __future__ import division
from datetime import datetime
from flask import render_template, Blueprint,redirect
from flask import request
from flask import current_app
import codecs,os
import sys,re
import logging
from urllib import urlopen
from lj_parser import lj_extractor
from graphh import richclub,ljgraph

def fetch_profile(x,platform):
    headers = { 'User-Agent' : 'Social network graph project;http://dev.rus-ltc.org/websocgraph' }
    blog = x.strip()
    print "Fetching profile of",blog+'...'
    if platform == "lj":
	if blog.startswith('_') or blog.endswith('_'):
	    content = urlopen('http://users.livejournal.com/%s/data/foaf' % blog,None,headers).read().decode('utf-8')
	else:
	    content = urlopen('http://%s.livejournal.com/data/foaf' % blog,None,headers).read().decode('utf-8')
    elif platform == "ljr":
	content = urlopen('http://lj.rossia.org/users/%s/data/foaf' % blog,None,headers).read().decode('utf-8')
    d = codecs.open('%s_profile' % blog, 'w+', 'utf-8')
    d.write(content)
    d.close()



websocgraph = Blueprint('websocgraph', __name__, template_folder='templates')


@websocgraph.route('/', methods=['POST','GET'])
def socanalyzer():
    if request.method == "POST":
	try:
	    argument  = request.form['blog']
	    argument2 = request.form['platform']
	    argprof = argument+"_profile"
	    os.chdir('/var/www/websocgraph/')
	    friends = []
	    friends.append(argument)
	    fulldata = []
	    if argument2 == "ljr":
		os.chdir('profiles/ljr')
	    elif argument2 == "lj":
		os.chdir('profiles/')
	    existing = os.listdir(".")

	    if not argprof in existing:
		fetch_profile(argument,argument2)

	    for line in codecs.open('%s_profile' % argument,'r','utf-8').readlines():
		res = line.strip()
		if res.startswith('<foaf:nick>'):
		    friend = re.sub('<.*?>','',res)
		    friendprof = friend+"_profile"
		    if friend != argument.strip() and friend != argument.strip().replace('_','-'):
			friends.append(friend)
    		    if not friendprof in existing:
			fetch_profile(friend,argument2)

	    for person in friends:
		data = lj_extractor(person)
		if person == argument:
		    userpic = data[4]
		fulldata.append(data)

	    output = ljgraph(fulldata,argument,argument2)
	    return render_template('wsg.html', blogger = argument, platform = argument2, userpic = userpic, vnumber1=output[0][0],enumber1=output[0][1],vmaxbet1=output[0][2][1],emaxbet1=output[0][3][2:],core1=output[0][4],vnumber2=output[1][0],enumber2=output[1][1],vmaxbet2=output[1][2][1],emaxbet2=output[1][3][2:],core2=output[1][4])
	except:
	    error_value = "Error!"
	    return render_template("wsg.html", error=error_value)
    return render_template("wsg.html")








