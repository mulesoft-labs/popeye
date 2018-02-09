#!/usr/bin/python2.7

'''

'''

import sys

import os.path

import logging


class PopEyeLogger:

  extra = {}
  region = "-"
  acctAlias = "-"
  logFile = None
  verbose = False
  debug = False

  def __init__(self, logFile=None, region="-", acctAlias="-", verbose=False, debug=False):
    self.region = region
    self.acctAlias = acctAlias
    self.logFile = logFile
    self.verbose = verbose
    self.debug = debug

  def createLogger(self):
    # This is a test to see if the logger is already configured, and if so remove it
    root = logging.getLogger()
    if root.handlers:
      for handler in root.handlers:
        root.removeHandler(handler)

    #self.extra = {'region': self.region, 'acctAlias': self.acctAlias}
    #logFormatter = logging.Formatter("%(asctime)s [%(threadName)-7.12s] [%(levelname)-5.9s] [%(acctAlias)s %(region)s] -  %(message)s")
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-7.12s] [%(levelname)-5.9s] -  %(message)s")
    logger1 = logging.getLogger()
    if self.debug:
      logger1.setLevel(logging.DEBUG)
    elif self.verbose:
      logger1.setLevel(logging.INFO)
    else:
      logger1.setLevel(logging.WARNING)

    if self.logFile is not None:
      # We want to write to a file
      logDir = os.path.dirname(self.logFile)
      if not os.path.exists(logDir):
        try:
          os.makedirs(logDir)
        except OSError as exception:
          print("Error, log directory: {0} does not exist and unable to create it".format(logDir))
          sys.exit(2)
      elif not os.path.isdir(logDir):
        print("Error, log path: {0} is not a directory".format(logDir))
        sys.exit(2)
      if not os.access(logDir, os.W_OK):
        print("Error, no write permissions to log directory: {0}".format(logDir))
        sys.exit(2)
      fileHandler = logging.handlers.RotatingFileHandler(self.logFile, maxBytes=20000, backupCount=10)
      fileHandler.setFormatter(logFormatter)
      logger1.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger1.addHandler(consoleHandler)

    #logger1 = logging.LoggerAdapter(logger1, self.extra)
    #logger1 = logging.LoggerAdapter(logger1)

    return logger1

  def setExtra(self, region=None, acctAlias=None):
    if region is not None:
      self.extra['region'] = region
    if acctAlias is not None:
      self.extra['acctAlias'] = acctAlias


