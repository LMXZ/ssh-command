from std import *
import os, sys, shutil

currentPath = os.path.dirname(os.path.abspath(__file__))
servicePath = f'{currentPath}/service'
pythonPath = sys.executable
serviceName = 'ssh-command'

def escapeTemplate(dir: str, templateFile: str, **kwargs):
    with open(f'{dir}/template-{templateFile}', 'r') as file:
        template = file.read()

    with open(f'{dir}/{templateFile}', 'w') as file:
        file.write(template.format(**kwargs))

escapeTemplate(servicePath, 'start-service.sh', pythonPath=pythonPath, currentPath=currentPath, serviceName=serviceName)
escapeTemplate(servicePath, f'{serviceName}.service', servicePath=servicePath, serviceName=serviceName)

try:
    os.system(f'sudo systemctl stop {serviceName}.service')
except:
    pass

try:
    print('registering')
    os.system(f'chmod 755 {servicePath}/start-service.sh')
    os.system(f'sudo cp "{servicePath}/{serviceName}.service" "/etc/systemd/system/"')
    os.system(f'sudo systemctl enable {serviceName}.service')
    os.system(f'sudo systemctl daemon-reload')
    os.system(f'sudo systemctl start {serviceName}.service')
except:
    print('register failed!')
    exit()

print('register succeed!')
