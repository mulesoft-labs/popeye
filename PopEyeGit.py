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
  repoDepth = 2

  def __init__(self, logger, target, src):
    self.logger = logger
    self.target = target
    self.src = src

  
  # This will clone the repo if it doesn't exist, if it does will pull the repo
  def cloneRepo(self):
  
    # This should be the path to the git file
    gitFile = os.path.join(self.target, '.git')
  
    if not os.path.isdir(gitFile):
      if os.path.isdir(self.target):
        self.logger.info("About the remove and recreate the clone directory")
        # directory exists so remove it
        shutil.rmtree(self.target)
        os.mkdirs(self.target)
      self.logger.info("About to clone the repo")
      # Clone the repo
      Repo.clone_from(self.src, self.target, depth=self.repoDepth)
      self.logger.info("Repo cloning has been completed")
  
    # Pull the repo
    self.pullRepo()
  
  
  # This will pull the repo
  def pullRepo(self):
  
    try:
  
      self.logger.info("About to perform a hard reset then a pull")
      repo = git.Repo(self.target)
      # remove any changes that have been made locally
      repo.git.reset("--hard", "origin/master")
      o = repo.remotes.origin
      o.fetch()
      repo.git.merge("origin/master")
      self.logger.info("Pull has been completed")
  
    except Exception, e:
      # Something has happened, unable to merge, send an error email
      serverHostName = socket.gethostname()
      errorMsg = str(e)
      self.logger.error("Error, unable to merge repo:\n{0}".format(str(e)))


  def commitPushRepo(self):
    self.logger.info("Need to commit the repo")
    repo = git.Repo(self.target)
    o = repo.remotes.origin

    file_list = [ 'Jenkinsfile' ]
    repo.index.add(file_list)
    repo.index.commit("update Jenkinsfile")

    try:
      self.logger.info("About to push")
      # remove any changes that have been made locally
      o.push()
      self.logger.info("Push has been completed")

    except Exception, e:
      # Something has happened, unable to merge, send an error email
      serverHostName = socket.gethostname()
      errorMsg = str(e)
      self.logger.error("Error, unable to push:\n{0}".format(str(e)))




