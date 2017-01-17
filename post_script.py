from bottle import Bottle, run, request, post
import pprint
import yaml
import os
import json
from jinja2 import Environment, FileSystemLoader
import urllib
from controller.controller import Controller

APP_PATH = os.path.dirname(os.path.realpath(__file__))
ENV = Environment(loader=FileSystemLoader('templates'))

app = Bottle()

ctrl = Controller()

@app.post('/hello/<repo>')
def hello(repo):
    body = request.body.read()
    jsonObj = json.loads(body)

    pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
    pp.pprint(jsonObj)

    #body = body.replace("+","").replace("payload=","")
    #parsedBody = urllib.unquote(body).decode('utf8')
    #jsonObj = json.loads(parsedBody)
    ctrl.preprovision(repo, jsonObj)

@app.get('/add/<repo>/<branch>')
def add(repo, branch):
    ctrl.provision(repo, branch)

def main():
    #with open("conf.yaml", "r") as fd:
    #    str = fd.read()
    #out = yaml.load(str)
    #print out
    #pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
    #pp.pprint(out)
    #print "\n\n"
    ctrl.start()

main()
try:
    run(app, host='0.0.0.0', port=8909)
except KeyboardInterrupt:
    ctrl.clean()
except Exception, e:
    print "Unexpected error"
    print e
