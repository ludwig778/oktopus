from bottle import Bottle, run, request, post
import pprint
import yaml
import json
import jinja2
import urllib

app = Bottle()

@app.post('/hello')
def hello():
    body = request.body.read()
    #body = body.replace("+","").replace("payload=","")
    #parsedBody = urllib.unquote(body).decode('utf8')
    #jsonObj = json.loads(parsedBody)
    jsonObj = json.loads(body)
    print jsonObj
    push_info = jsonObj['push']['changes'][0]['new']
    branch = push_info['name']
    message = push_info['target']['message']
    user = push_info['target']['author']['raw']
    repo = jsonObj['repository']['name']
    print "Webhook received, repo: {0} : branch {1}".format(repo, branch)
    print "                  user: {0}".format(user)
    print "               message: {0}".format(message)

def main():
    print "hello"

    with open("conf.yaml", "r") as fd:
        str = fd.read()
    out = yaml.load(str)
    #print out
    pp = pprint.PrettyPrinter(indent=1, width=80, depth=None, stream=None)
    #pp.pprint(out) 
    #print "\n\n"
    for domain in out['domains']:
        for app in out['domains'][domain]:
            print app

main()
run(app, host='0.0.0.0', port=8080)
