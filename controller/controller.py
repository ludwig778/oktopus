import os
import docker
from git import Repo
import yaml
from jinja2 import Environment, FileSystemLoader

APP_PATH = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))

ENV = Environment(loader=FileSystemLoader(APP_PATH + '/templates'))
TEMPLATE = ENV.get_template("base.conf")

CONFIG = os.path.abspath(os.path.join(APP_PATH, "config", "conf.yml"))

NGINX_CONF_PATH = os.path.abspath(os.path.join(APP_PATH, "controller", "nginx_conf"))
BASE_REPOS_PATH = os.path.abspath(os.path.join("/", "var", "opt", "git_repos"))

class Controller:

    file_confs = {}
    def __init__(self):
        with open(CONFIG, "r") as fd:
            self.datas = yaml.load(fd.read())

        if not self.datas:
            print("Error importing the yaml file")
            exit()

        self.client = docker.from_env()
    
    def start(self, environment="prod"):
        for app in self.datas['apps']:
            #print args
            # WRAPPER PROVISIONNING
            self.provision(app, environment)
            # IF OK RUN CONTAINER

    def get_latest_code(url, repo, branch):
        print url, repo, branch
        checkout_to = branch
        if False:
            if branch not in ["master", "preprod"]:
                branch = "test"
            repo_folder = os.path.join(BASE_REPOS_PATH, repo, branch)
             
            if not os.path.exists(repo_folder):
                Repo.clone_from(url, repo_folder)
                repo = Git(repo_folder)
            else:
                repo = Git(repo_folder)
                repo.pull()
            repo.checkout(checkout_to)
    
    def provision(self, app, environment):
        args = self.datas['apps'][app]
        if not args['git'] and False:
            return 0

        if environment == "prod":
            branch = "master"
        elif environment == "preprod":
            branch = "preprod"
        else:
            branch = "any"

        #output = TEMPLATE.render(args=args, env=environment)
        filename = "{0}_{1}.conf".format(args['name'], environment)
        #with open(NGINX_CONF_PATH + "/" + filename, "wb") as fh:
        #    fh.write(output)

        try:
            self.file_confs[environment].append(args['name'])
        except:
            self.file_confs[environment] = [args['name']]

        #print args
        print "{0} @ {1}/{2}".format("output", NGINX_CONF_PATH, filename)
        print "Git clone/pull from: {0}".format(args['git'])
        print "docker build -t {0}:{1} {2}/{0}/{1}/".format(args['name'], environment, BASE_REPOS_PATH)
        #print ""
        volumes = {}
        ports = {}
        if args['connect']['method'] == "sock_file":
            volumes.update({'/var/host/sockets_storage/{0}/{1}/'.format(args['name'], environment):
                            {'bind': args['connect']['arg'],
                             'mode': 'ro'}})
        else:
            ports.update({'{0}/tcp'.format(args['connect']['arg']): args['connect']['arg']})

        print "docker run {0}:{1}\nvolumes={2}\nports={3}".format(args['name'], environment, volumes, ports)
        print ""



    def build_container(repo, branch):
        self.client.images.build(path=os.path.join(BASE_REPOS_PATH, repo, branch), tag="%s:%s" % (repo, branch))
    
    def run_container(app, repo, branch):
        ports = {}
        volumes = {'/tmp/socket/folder/host': {}}
        self.client.containers.run(image="%s:%s" % (repo, branch),
                           command="nc -l -p 1111",
                           ports=ports,
                           volumes=volumes,
                           remove=True,
                           name="%s:%s" % (repo, branch))

    def clean():
        pass

if True:
    t = Controller()
    t.start()
    print t.file_confs



