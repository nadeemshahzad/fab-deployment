from fabric.api import *
import sys
from importlib import import_module

conf={}
try:
    """
    Import module
    """
    sys.path.append('/home/ubuntu/.Fabric')
    conf=import_module("settings").FABRIC
except ImportError:
    print ("Aborting, error importing enviroment settings")
    sys.exit()

env.key_filename=conf['SSH_KEY']                                                                                                                                                                                                 
env.port=conf['SSH_PORT']                                                                                                                                                                                                        
env.proj_path=conf['PROJECT_PATH']                                                                                                                                                                                               
env.static_path=conf['STATIC_BUILD_PATH']                                                                                                                                                                                        
env.gateway_instance=conf['GATEWAY_INSTANCE']                                                                                                                                                                                    
env.cron_instance=conf['CRON_INSTANCE']                                                                                                                                                                                          
                                                                                                                                                                                                                                 

@hosts('localhost')                                                                                                                                                                                                              
def deploy_web(branch):              
    """                                                                                                                                                                                                  
    Run migrations, install repo-name-provider and build static                                                                                                                                                                       """                                                                                                                                                                                                                          
    with lcd(env.proj_path):                                                                                                                                                                                                     
        local('git pull -v --progress')                                                                                                                                                                                          
        local('python3.5 manage.py migrate')                                                                                                                                                                                     
        local("find %s -name '*.pyc' -exec rm -rf {} \;" % env.proj_path)
        local('chown -R www-data:www-data %s' % env.proj_path)
    try:
        local('python3.5 -m pip uninstall repo-name-provider -y')
    except:
        pass
    local('python3.5 -m pip install git+ssh://git@github.com/repo-name/provider.git@%s' % branch)
    build_static()
    local("service uwsgi restart")
    local("service nginx restart")
    local("supervisorctl restart all")

@hosts('localhost')
def build_static():
    """
    Build static directory.
    """
    with lcd(env.static_path):
         local('/usr/local/bin/node-v0.12.2-linux-x64/bin/node r.js -o build.js')

    
def deploy_cron(branch):
    
    if env.cron_instance:
        with settings(host_string=env.cron_instance):
            env.user='ubuntu'
            with cd(env.proj_path):
                sudo('git pull -v --progress')
            install_provider(branch)
    else:
         pass

def deploy_gateway(branch):
    
    for host in env.gateway_instance:
        with settings(host_string=host):
             env.user='ubuntu'
             install_provider(branch)

def install_provider(branch):
     """ 
     Install provider-repository
     """
     try:
         sudo('python3.5 -m pip uninstall repo-name-provider -y')
     except:
         pass
     sudo('python3.5 -m pip install git+ssh://git@github.com/repo-name/provider.git@%s' % branch)
     sudo('service supervisor restart')

def deploy(branch):
    deploy_web(branch)
    deploy_gateway(branch)
    deploy_cron(branch)
