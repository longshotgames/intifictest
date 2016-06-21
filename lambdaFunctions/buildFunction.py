#!/usr/bin/python

import json
import os
import subprocess
import sys
import zipfile

def zipdir(path, zipf):
    for root, dirs, files in os.walk(path):
        for f in files:
            zFile = os.path.join(path,f)
            zPath = zFile[zFile.find(os.path.sep)+1:]
            zipf.write(zFile, zPath)

def publishFunction(subDir, region, branch):
    zipf = zipfile.ZipFile('package.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(subDir, zipf)
    zipf.close()

    cmd = "aws lambda update-function-code --region " + region + " --function-name " + subDir + " --zip-file fileb://package.zip"
    subprocess.check_output(cmd, shell=True)

    cmd = "aws lambda publish-version --region " + region + " --function-name " + subDir 
    subprocess.check_output(cmd, shell=True)

    cmd = "aws lambda list-versions-by-function --region " + region + " --function-name " + subDir
    versions = subprocess.check_output(cmd, shell=True)
    versionsJson = json.loads(versions)
    versionNum = 0
    for version in versionsJson['Versions']:
        try:
            if (int(version['Version']) > versionNum):
                versionNum = int(version['Version'])
        except:
            print "skipping " + version['Version']
    cmd = "aws lambda upate-alias --region " + region + " --function-name " + subDir + " --name " + branch + " --function-version " + str(versionNum)
    subprocess.check_output(cmd, shell=True)

if __name__ == "__main__":
    if (len(sys.argv) != 4):
        print 'ERROR - command line:  buildFunction.py functionSubDir region branch'
        sys.exit(1)


    publishFunction(sys.argv[1], sys.argv[2], sys.argv[3])



