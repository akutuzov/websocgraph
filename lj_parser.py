#!/bin/python
# coding: utf-8
# extracting blogger info from lj(r) profile
import codecs,re

def lj_extractor(x):
    filename = x+'_profile'
    profile = codecs.open(filename,'r+','utf-8').readlines()
    posts = 0
    comments_received = 0
    reads = []
    pics = []
    for line in profile:
	res = line.strip()
	if res.startswith('<ya:posted>'):
	    num = re.sub('<.*?>','',res)
	    posts = int(num)
	    continue
	if res.startswith('<ya:received>'):
	    num = re.sub('<.*?>','',res)
	    comments_received += int(num)
	    continue
	if res.startswith('<foaf:nick>'):
	    friend = re.sub('<.*?>','',res)
	    if friend != x:
		reads.append(friend)
	    continue
	if res.startswith('<foaf:img'):
	    res2 = res.replace('<foaf:img rdf:resource="','')
	    pics.append(res2[:-4])
	    continue
    return x,posts,comments_received,','.join(reads),pics