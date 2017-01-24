import os
import docker
import json
import requests
from time import sleep
from git import Repo, Git
import yaml
from jinja2 import Environment, FileSystemLoader

APP_PATH = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))

ENV = Environment(loader=FileSystemLoader(APP_PATH + '/templates'))
TEMPLATE = ENV.get_template("base.conf")

CONFIG = os.path.abspath(os.path.join(APP_PATH, "config", "conf.yml"))

PARENT_DIR_PATH = os.path.abspath('..')
BASE_REPOS_PATH = os.path.join(PARENT_DIR_PATH, "git_repos")
BASE_SOCKETS_PATH = os.path.join(PARENT_DIR_PATH, "socket_storage")
NGINX_CONF_PATH = os.path.join(PARENT_DIR_PATH, "nginx_conf")


class Controller:

    file_confs = {}
    def __init__(self):
        with open(CONFIG, "r") as fd:
            self.datas = yaml.load(fd.read())

        if not self.datas:
            print("Error importing the yaml file")
            exit()

        self.client = docker.from_env()
      
    def cleanup(self, name):  
        print "Cleanup " + name
        for i in range(0, 3):
            try:
                container = self.client.containers.get(name)
                container.stop()
                container.remove()
            except docker.errors.NotFound:
                return
            except requests.exceptions.ReadTimeout:
                pass
            except Exception, e:
                print "ERROR"
                print e
                if i == 2:
                    print "Too much error, quiting..."
                    exit(1)
        print "Flushing done"

    def start(self):
        print "Erasing previous nginx confs..."
        fileList = os.listdir(NGINX_CONF_PATH)
        for fileName in fileList:
            os.remove(NGINX_CONF_PATH+"/"+fileName)

        for app in self.datas['apps']:
            self.provision(app)

        self.start_nginx()

        output = ENV.get_template("default.conf").render()
        with open(NGINX_CONF_PATH + "/default.conf", "wb") as fh:
            fh.write(output)

        print "Cleaning...."
        for i in self.client.images.list():
            if not i.tags:
                self.client.images.remove(i.attrs)
        print "Done"

    def start_nginx(self):
        print "Creating nginx container"
        self.cleanup("mynginx")

        nginx = self.client.containers.create(image="nginx",
                                   ports={'80/tcp': 80},
                                   volumes={NGINX_CONF_PATH:
                                                   {'bind': "/etc/nginx/conf.d",
                                                    'mode': 'rw'},
                                            BASE_SOCKETS_PATH:
                                                   {'bind': "/sockets",
                                                    'mode': 'rw'}},
                                   detach=True,
                                   name="mynginx",
                                   hostname="mynginx")
        self.client.networks.get("my_bridge").connect("mynginx")
        self.client.networks.get("bridge").disconnect("mynginx")
        nginx.start()
    
    def restart_nginx(self):
        print "Restarting nginx container"
        nginx = self.client.containers.get("mynginx")
        nginx.restart()

    def stop_container(self, name, environment):
        print "Stop container {0}_{1}".format(name, environment)
        container = self.client.containers.get("{0}_{1}".format(name, environment))
        print "container flushing: " + container.name
        container.stop()
        container.remove()

    def provision(self, app, branch="master"):
        print "Provisioning " + app + " @ branch " + branch
        try:
            args = self.datas['apps'][app]
        except:
            return 0

        if not args['git']['url'] and False:
            return 0

        if branch == 'master':
            environment = 'prod'
        else:
            environment = 'preprod' if branch == 'preprod' else 'test'
            try:
                to_stop = self.file_confs[environment][0]
                self.stop_container(to_stop, environment)
                self.file_confs[environment] = []
            except Exception, e:
                print e
                pass

#        print args
        filename = "{0}_{1}.conf".format(args['name'], environment)
        self.cleanup("{0}_{1}".format(args['name'], environment))

        output = TEMPLATE.render(args=args, env=environment)
        with open(NGINX_CONF_PATH + "/" + filename, "wb") as fh:
            fh.write(output)
#        print filename
#        print output
        try:
            if not args['name'] in self.file_confs[environment]:
                self.file_confs[environment].append(args['name'])
        except:
            self.file_confs[environment] = [args['name']]
        repo_folder = os.path.join(BASE_REPOS_PATH, args['name'], environment)
        #print "{0} @ {1}/{2}".format("output", NGINX_CONF_PATH, filename)
        #print "Git clone/pull from: {0}".format(args['git'])
        #print "Repo to {0}".format(repo_folder)
        if False:
            if not os.path.exists(repo_folder):
                Repo.clone_from(args['git']['url'], repo_folder)
                repo = Git(repo_folder)
            else:
                repo = Git(repo_folder)
                repo.pull()
            repo.checkout(branch)

        print "docker build -t {0}:{1} {2}/{0}/{1}/".format(args['name'], environment, BASE_REPOS_PATH)
        tt = self.client.images.build(path=os.path.join(BASE_REPOS_PATH, args['name'], environment),
                          tag="%s_%s" % (args['name'], environment),
                          stream=True,
                          rm=True,
                          forcerm=True)

#        print "Already build"
        volumes = {}
        ports = {}
        if args['connect']['method'] == "sock_file":
            socket_folder = BASE_SOCKETS_PATH + '/{0}/{1}/'.format(args['name'], environment)
            if not os.path.exists(socket_folder):
                os.makedirs(socket_folder)
            volumes.update({socket_folder:
                            {'bind': args['connect']['arg'],
                             'mode': 'rw'}})
                             
        container = self.client.containers.create(image="%s_%s" % (args['name'], environment),
                                   ports=ports,
                                   volumes=volumes,
                                   detach=True,
                                   name="%s_%s" % (args['name'], environment),
                                   hostname="%s-%s" % (args['name'], environment))
        self.client.networks.get("my_bridge").connect("%s_%s" % (args['name'], environment))
        self.client.networks.get("bridge").disconnect("%s_%s" % (args['name'], environment))
        container.start()
        print "Containers:"
        print self.file_confs

    def clean_all(self):
        print "Clean all containers"
        for container in self.client.containers.list():
            if container.name.split('_')[0] in self.datas['apps'].keys():
                self.cleanup(container.name)

    def preprovision(self, repo, webhook):
        datas = ""
        for i in self.datas['apps']:
            if self.datas['apps'][i]['name'] == repo:
                datas = self.datas['apps'][i]

        if not datas:
            print "Not a valid webhook name" + repo
            return False

        webhook_type = datas['git']['type']
        if webhook_type == "bitbucket":
            push_info = webhook['push']['changes'][0]['new']
            branch = push_info['name']
            message = push_info['target']['message']
            user = push_info['target']['author']['raw']
            repo2 = webhook['repository']['name']
        elif webhook_type == "gogs":
            branch = webhook['ref'].split('/')[-1]
            repo2 = webhook['repository']['name']
            user = webhook['commits'][0]['committer']['name']
            message = webhook['commits'][0]['message']
        elif webhook_type == "github":
            branch = webhook['ref'].split('/')[-1]
            repo2 = webhook['repository']['name']
            user = webhook['pusher']['name']
            message = webhook['head_commit']['message']
        print "Webhook received, repo: {0} : branch {1}".format(repo2, branch)
        print "                  user: {0}".format(user)
        print "               message: {0}".format(message)
        self.provision(repo, branch)
        self.restart_nginx()
