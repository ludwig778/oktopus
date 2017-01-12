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
    
    def start(self):
        for app in self.datas['apps']:
            self.provision(app)

    def provision(self, app, branch="master"):
        args = self.datas['apps'][app]
        if not args['git'] and False:
            return 0

        print "Original branch: {0}".format(branch)
        if branch == 'master':
            environment = 'prod'
        else:
            environment = 'preprod' if branch == 'preprod' else 'test'
            try:
                to_stop = self.file_confs[environment][0]
                print "Stop container {0}:{1}".format(to_stop, environment)
                self.file_confs[environment] = []
            except:
                pass


        filename = "{0}_{1}.conf".format(args['name'], environment)
        # output = TEMPLATE.render(args=args, env=environment)
        # with open(NGINX_CONF_PATH + "/" + filename, "wb") as fh:
        #     fh.write(output)

        try:
            self.file_confs[environment].append(args['name'])
        except:
            self.file_confs[environment] = [args['name']]

        #print args


        repo_folder = os.path.join(BASE_REPOS_PATH, args['name'], environment)
        #print "{0} @ {1}/{2}".format("output", NGINX_CONF_PATH, filename)
        #print "Git clone/pull from: {0}".format(args['git'])
        #print "Repo to {0}".format(repo_folder)
        if False:
             
            if not os.path.exists(repo_folder):
                Repo.clone_from(args['git'], repo_folder)
                repo = Git(repo_folder)
            else:
                repo = Git(repo_folder)
                repo.pull()
            repo.checkout(branch)

        
        print "docker build -t {0}:{1} {2}/{0}/{1}/".format(args['name'], environment, BASE_REPOS_PATH)
        #self.client.images.build(path=os.path.join(BASE_REPOS_PATH, args['name'], environment),
        #                         tag="%s:%s" % (args['name'], environment))
        #print ""
        volumes = {}
        ports = {}
        if args['connect']['method'] == "sock_file":
            volumes.update({'/var/host/sockets_storage/{0}/{1}/'.format(args['name'], environment):
                            {'bind': args['connect']['arg'],
                             'mode': 'ro'}})
        else:
            ports.update({'{0}/tcp'.format(args['connect']['arg']): args['connect']['arg']})


        #self.client.containers.run(image="%s:%s" % (repo, branch),
        #                           ports=ports,
        #                           volumes=volumes,
        #                           remove=True,
        #                           name="%s:%s" % (repo, branch))

        print "docker run -rm\n--volumes={2}\n--ports={3}\n--name={0}:{1}\n {0}:{1}".format(args['name'], environment, volumes, ports)
        print ""

    def clean(self):
        pass

if True:
    t = Controller()
    t.start()
    t.provision("fake", "test")
    t.provision("fake", "preprod")
    t.provision("main", "nope")
    t.provision("app", "okay_branch")
    t.provision("main", "tchootchoo")
    t.provision("main", "wtf")
    print t.file_confs



