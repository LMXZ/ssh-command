pythonPath={pythonPath}
currentPath={currentPath}
serviceName={serviceName}

echo $currentPath
cd $currentPath
sudo $pythonPath "$currentPath/$serviceName.py"
