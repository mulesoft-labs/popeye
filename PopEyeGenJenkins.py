#!/usr/bin/python

import sys
import time
import os
import platform
import subprocess
from socket import socket
import urllib2
from optparse import OptionParser
import ast
import re
import traceback
#import random
#import requests

from datetime import datetime

import socket

from git import Repo
import git

import shutil

from PopEyeLogger import PopEyeLogger
from PopEyeGit import PopEyeGit



class PopEyeGenJenkins:

  logger = None
  verbose = False
  aws_key = None
  aws_secret = None
  targetDir = "/home/ubuntu/popeye-trigger"
  srcRepo = "git@github.com:mulesoft-ops/popeye-trigger.git"
  environment = None


  def __init__(self, environment, targetDir=None, srcRepo=None, verbose=False, aws_key=None, aws_secret=None):
    self.verbose = verbose
    self.aws_key = aws_key
    self.aws_secret = aws_secret
    if targetDir is not None:
      self.targetDir = targetDir
    if srcRepo is not None:
      self.srcRepo = srcRepo

    self.environment = environment
    
    popLogger = PopEyeLogger(verbose=self.verbose)
    self.logger = popLogger.createLogger()

    
  def startSQS(self, sqsQueue):

     poppySQS = PopEyeSQS(aws_key=self.aws_key, aws_secret=self.aws_secret)
     while True:
       msgList = poppySQS.fetchFromSQS(sqsQueue)
       if len(msgList) > 0:
         # We have had a message come in
         self.logger.info("Messages have arrived, now need to process")
         for sqsMsg in msgList:
           if "Body" in sqsMsg:
             msgBody = sqsMsg["Body"]
             msgObj = json.loads(msgBody)
       time.sleep(1) 



  def processMessage(self, msgObj):
    # We take an object and start to process it, defined in jsonformat.txt
    if "data" in msgObj:
      msgData = msgObj["data"]
    if "releasetag" in msgObj:
      releaseTag = msgObj["releasetag"]


  def startDeploy(self, buildNumber, jsonObj):
    poppyGitObj = PopEyeGit(self.logger, self.targetDir, self.srcRepo)
    poppyGitObj.cloneRepo()

    self.buildFile(buildNumber, jsonObj)

    poppyGitObj.commitPushRepo()


  def buildFile(self, buildNumber, jsonObj):
    jenkinsFilePath = os.path.join(self.targetDir, "Jenkinsfile")
    f = open('jenkinsFileTemplate', 'r')
    jenkinsTemp = f.read()

    w = open(jenkinsFilePath, 'w')

    dateLine = "// " + str(datetime.now()) + "\n\n"
    w.write(dateLine)

    buildLine = "jenkinsbuildnumber = \"" + buildNumber + "\"\n"
    w.write(buildLine)

    deployLine = "deployEnv = \"" + self.environment + "\"\n"
    w.write(deployLine)
    
    jsonObjLine = "def jobs = " + jsonObj + "\n"
    w.write(jsonObjLine)

    w.write(jenkinsTemp)

    w.close()



if __name__ == "__main__":


  usage = "usage: %prog [ options ] arg"
  parser = OptionParser(usage)
  parser.add_option("-s", "--src", action="store", dest="src", help="Source repo that we want to get clone or pull from")
  parser.add_option("-t", "--target", action="store", dest="target", help="Target directory we want to place the repo into")
  parser.add_option("-D", "--depth", action="store", dest="repoDepth", type="int", default=2, help="Depth of repo, default is 2")
  parser.add_option("-v", "--verbose", help="Print verbose, will print info messages", action="store_true", default=False)

  (options, args) = parser.parse_args()
  src = options.src
  target = options.target

  verbose = options.verbose


  '''
  if src is None:
    print("Error, repo must be specified with -s or --src")
    parser.print_help()
    sys.exit()

  if target is None:
    print("Error, target local directory must be sepecified with -t or --target")
    parser.print_help()
    sys.exit()
  '''

  buildNumber = "PCCR-655"
  jsonObj = '[["name":"core-services","build":1, "deploy_time":1, "test_time":2, "test_success": false, "deploy_success": true],["name":"exchange","build":2, "deploy_time":1, "test_time":2, "test_success": true, "deploy_success": true]]'

  poppyJenkObj = PopEyeGenJenkins("QAX")  
  poppyJenkObj.startDeploy(buildNumber, jsonObj)


