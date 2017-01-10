import os
import yaml
from git_helper import manage_repo
from jinja2 import Environment, FileSystemLoader

APP_PATH = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))

ENV = Environment(loader=FileSystemLoader(APP_PATH + '/templates'))
TEMPLATE = ENV.get_template("base.conf")

CONFIG = os.path.abspath(os.path.join(APP_PATH, "config", "conf.yml"))

NGINX_CONF_PATH = os.path.abspath(os.path.join(APP_PATH, "controller", "nginx_conf"))


class BaseController:

    file_confs = {}
    def __init__(self):
        with open(CONFIG, "r") as fd:
            self.datas = yaml.load(fd.read())

        if not self.datas:
            print("Error importing the yaml file")
            exit()

    def generate_all(self, environment="prod"):
    
        for domain in self.datas['domains']:
            domain_data = self.datas['domains'][domain]
            for app in domain_data:
                args = domain_data[app]
                if not args['git'] and False:
                    continue 
                args.update({"name": app})
                #print args
                
                manage_repo(args['git'], app, "master")


                # CHECK IF DOCKER BUILD OK OR WHATEVER

                self.create(args, environment)

                # IF OK RUN CONTAINER

    
    def create(self, args, environment):
        output = TEMPLATE.render(args=args, env=environment)
        filename = "{0}_{1}.conf".format(args['name'], environment)
        with open(NGINX_CONF_PATH + "/" + filename, "wb") as fh:
            fh.write(output)

        if self.file_confs.has_key(args['name']):
            self.file_confs[args['name']] += [environment]
        else:
            self.file_confs[args['name']] = [environment]
        
        print "{0}\n@ {1}/{2}".format("output", NGINX_CONF_PATH, filename)

    def clean():
        pass

t = BaseController()
t.generate_all()
print t.file_confs