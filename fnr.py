import os
import redis
from flask import Flask
from flask import jsonify
from flask_cors import CORS
from flask import request
import json
import pandas as pd
app = Flask(__name__)
CORS(app)
db=redis.Redis(host='127.0.0.1', charset="utf-8", decode_responses=True, db=0)
db1=redis.Redis(host='127.0.0.1', charset="utf-8", decode_responses=True, db=1)

@app.route('/')
def hello_world():
    d = db.keys()
    #q = [ rec.decode('ascii') for rec in d ]
    return jsonify(d)

@app.route('/details/<aaa>') 
def details(aaa):
    d = db.hgetall(aaa)
    #q = { y.decode('ascii'): d.get(y).decode('ascii') for y in d.keys() }
    return  jsonify(d)

@app.route('/quotes/<aaa>') 
def quotes(aaa):
    d = db1.hgetall(aaa)
    #print(d, type(d['qts']), json.loads(d['qts']))
    #print(d['qts'])
    #q = { y.decode('ascii'): d.get(y).decode('ascii') for y in d.keys() } 
    return  jsonify(json.loads(d['qts']))

@app.route('/quotes_hist/<aaa>') 
def quotes_hist(aaa):
    d = db1.hgetall(aaa+"_hist")
    #print(d, type(d['qts']), json.loads(d['qts']))
    #print(d['qts'])
    #q = { y.decode('ascii'): d.get(y).decode('ascii') for y in d.keys() }
    return  jsonify(json.loads(d['qts']))

@app.route('/chartkeys') 
def chart_keys():
    keys = db1.keys()
    nk={}
    for rec in keys:
        #print(rec)
        if "_hist" in rec: continue
        if "_anl" in rec: continue
        details = db.hgetall(rec)
        
        anl = db1.hgetall(rec+"_anl")
        for anl_rec in anl:
            details[anl_rec]=anl[anl_rec]
        
        nk[rec]=details
        
    #print(nk)
    return jsonify(nk)


@app.route('/tbl') 
def tbl():
    keys = db.keys()
    lst = []
    for i in range(len(keys)):
        el = db.hgetall(keys[i])
        if 'norm_cap' in el and 'optionable' in el:
            el['norm_cap']=float(el['norm_cap'])
            el['name']=keys[i]
            el['avl']=float( el['avl'].replace(',','') )
            #el['pb']=float( el['pb'].replace(',','') )
            #el['pe']=float( el['pe'].replace(',','') )
            #anl = db.hgetall(keys[i]+"_anl")
            #for rec in anl:
            #    el[rec]=anl[rec]
            if el['norm_cap']<2000000 and el['norm_cap']>20000 and el['avl']>0:
                lst.append(el)
        #if i >= 50:
        #    #    print(el)
        #break
    print(lst[1])
    #for j in range(len(lst)):
    #    rec = lst[j]
    #    if 'norm_cap' in rec:
    #        rec['norm_cap'] = float(rec['norm_cap'])
    #    else:
    #        rec['norm_cap'] = -1
    #    rec['name']=keys[j]
    
    dd = sorted(lst, key = lambda i: i['norm_cap'], reverse=True) 
        
    #q = { y.decode('ascii'): d.get(y).decode('ascii') for y in d.keys() }
    
    return jsonify(dd)

@app.route('/keys_only') 
def keys_only():
    keys = db.keys()
    lst = []
    for i in range(len(keys)):
        el = db.hgetall(keys[i])
        if 'norm_cap' in el and 'optionable' in el:
            el['norm_cap']=float(el['norm_cap'])
            el['name']=keys[i]
            el['avl']=float( el['avl'].replace(',','') )
            #el['pb']=float( el['pb'].replace(',','') )
            #el['pe']=float( el['pe'].replace(',','') )
            
            if el['norm_cap']<2000000 and el['norm_cap']>20000 and el['avl']>0:
                lst.append(el)
    
    dd = sorted(lst, key = lambda i: i['norm_cap'], reverse=True)
    dd2=[rec['name'] for rec in dd]
    
    return jsonify(dd2)

@app.route('/setname/<name>')
def setname(name):
    #db.set('name',name)
    return 'Name updated.'

@app.route('/setdetails/<name>')
def setdetails(name):
    print(name)
    #db.set('name',name)
    optionable = request.args.get('optionable')
    beta = request.args.get('beta')
    print(name, optionable, beta)
    el = db.hgetall(name)
    el['optionable']=optionable
    if beta!='-':
        el['beta']=float(beta)
    else:
        el['beta']=0
        
    db.hmset(name, el)
    return 'Name updated. {} {}'.format(optionable, beta)

if __name__ == '__main__':
    #app.run(host= '0.0.0.0', port='5055', ssl_context=('/home/greed/mycert.pem', '/home/greed/mykey.key'))
    app.run(host= '0.0.0.0', port='5055', ssl_context=('/home/greed/le_fullchain.pem', '/home/greed/le_privkey.pem'))
    
