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

@app.post('/hello')
def hello():
    body = request.body.read()
    #body = body.replace("+","").replace("payload=","")
    #parsedBody = urllib.unquote(body).decode('utf8')
    #jsonObj = json.loads(parsedBody)
    jsonObj = json.loads(body)
    print jsonObj

    repo = "gogs"
    if repo == "bitbucket":
        push_info = jsonObj['push']['changes'][0]['new']
        branch = push_info['name']
        message = push_info['target']['message']
        user = push_info['target']['author']['raw']
        repo = jsonObj['repository']['name']
    elif repo == "gogs":
        branch = jsonObj['ref'].split('/')[-1]
        repo = jsonObj['repository']['name']
        user = jsonObj['commits'][0]['committer']['name']
        message = jsonObj['commits'][0]['message']
    print "Webhook received, repo: {0} : branch {1}".format(repo, branch)
    print "                  user: {0}".format(user)
    print "               message: {0}".format(message)

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
