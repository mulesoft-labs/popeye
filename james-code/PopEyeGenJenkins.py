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

  def __init__(self, verbose=False, aws_key=None, aws_secret=None):
    self.verbose = verbose
    self.aws_key = aws_key
    self.aws_secret = aws_secret
    
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


  def buildFile(self, buildNumber, jsonObj):
    f = open('jenkinsFileTemplate', 'r')
    jenkinsTemp = f.read()

    w = open('JenkinsFile', 'w')
    buildLine = "jenkinsbuildnumber = \"" + buildNumber + "\""
    w.write(buildLine)
    
    jsonObjLine = "def jobs = " + jsonObj
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


  if src is None:
    print("Error, repo must be specified with -s or --src")
    parser.print_help()
    sys.exit()

  if target is None:
    print("Error, target local directory must be sepecified with -t or --target")
    parser.print_help()
    sys.exit()


  # This should be the path to the git file
  gitFile = os.path.join(target, '.git')
  
  # Always run a clone the repo when we first start the app to ensure the repo is there and up-to-date
  cloneRepo(target, src)

  # Start the timer
  startTimer(target, src)

  


