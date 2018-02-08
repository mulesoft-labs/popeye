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



class PopEyeGit:

  logger = None
  target = None
  src = None

  def __init__(self, logger, target, src):
    self.logger = logger
    self.target = target
    self.src = src

  
  # This will clone the repo if it doesn't exist, if it does will pull the repo
  def cloneRepo(self):
  
  
    # This should be the path to the git file
    gitFile = os.path.join(target, '.git')
  
    if not os.path.isdir(gitFile):
      if os.path.isdir(target):
        self.logger.info("About the remove and recreate the clone directory")
        # directory exists so remove it
        shutil.rmtree(target)
        os.mkdirs(target)
      self.logger.info("About to clone the repo")
      # Clone the repo
      Repo.clone_from(self.src, self.target, depth=_repoDepth)
      self.logger.info("Repo cloning has been completed")
  
    # Pull the repo
    self.pullRepo(self.target, self.src)
  
  
  # This will pull the repo
  def pullRepo(self, self.target, self.src):
  
    global debug
  
    try:
  
      if debug:
        print("About to perform a hard reset then a pull")
      repo = git.Repo(target)
      # remove any changes that have been made locally
      repo.git.reset("--hard", "origin/master")
      o = repo.remotes.origin
      #o.pull()
      #o.fetch(depth=_repoDepth)
      o.fetch()
      repo.git.merge("origin/master")
      if debug:
        self.logger("Pull has been completed")
  
    except Exception, e:
      # Something has happened, unable to merge, send an error email
      serverHostName = socket.gethostname()
      errorMsg = str(e)
      self.logger.error("Error, unable to merge repo:\n{0}".format(str(e)))




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

  


