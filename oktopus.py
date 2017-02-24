from bottle import Bottle, run, request, post
import pprint
import yaml
import os
import json
from jinja2 import Environment, FileSystemLoader
import urllib
from controller.controller import Controller

app = Bottle()

ctrl = Controller()

@app.post('/hello/<repo>')
def hello(repo):
    body = request.body.read()
    jsonObj = json.loads(body)
    pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
    pp.pprint(jsonObj)
    ctrl.preprovision(repo, jsonObj)

@app.get('/add/<repo>/<branch>')
def add(repo, branch):
    ctrl.provision(repo, branch)
    ctrl.restart_nginx()

def main():
    ctrl.clean_all()
    ctrl.cleanup("mynginx")
    ctrl.start()

main()
try:
    run(app, host='0.0.0.0', port=8909)
except KeyboardInterrupt:
    print "Keyboard escape"
    ctrl.clean_all()
    ctrl.cleanup("mynginx")
except Exception, e:
    print "Unexpected error"
    print e
