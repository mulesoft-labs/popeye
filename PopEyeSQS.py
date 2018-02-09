#!/usr/bin/python2.7

'''
Class to get messages in and out of SQS
'''

import json
import boto3
from botocore.exceptions import ClientError


class PopEyeSQS:

  profile = None
  region = None
  verbose = False
  debug = False
  logger = None
  aws_key = None
  aws_secret = None

  def __init__(self, logger, region="us-east-1", profile=None, aws_key=None, aws_secret=None, verbose=False, debug=False):
    self.profile = profile
    self.region = region
    self.debug = debug
    self.verbose = verbose
    self.logger = logger
    self.aws_key = aws_key
    self.aws_secret = aws_secret



  '''
  Generate the SQS client
  '''
  def genSQSClient(self):
    sqssession = None
    if self.profile is not None:
      sqssession = boto3.Session(profile_name=self.profile, region_name=self.region)
    elif self.aws_key is not None and self.aws_secret is not None:
      sqssession = boto3.Session(aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret, region_name=self.region)
    else:
      sqssession = boto3.Session(region_name=self.region)
    sqsclient = sqssession.client('sqs')
    return sqsclient
    

  '''
  Put a message into SQS. Firstly get the queue url based on the sqsQueue prefix and then add to sqs
  '''
  def sendToSQS(self, nameSpace, textContent, sqsQueue):
    sqsclient = self.genSQSClient()
    sqsDict = { "Key": nameSpace, "content": textContent }
    qResp = sqsclient.list_queues( QueueNamePrefix=sqsQueue )
    if "QueueUrls" in qResp:
      urlList = qResp["QueueUrls"]
      if len(urlList) == 1:
        sqsURL = urlList[0]
        contentStr = json.dumps(sqsDict)
        response = sqsclient.send_message(QueueUrl=sqsURL, MessageBody=contentStr)
    

  ''' 
  Fetch the messages from SQS
  '''
  def fetchFromSQS(self, sqsQueue):
    sqsclient = self.genSQSClient()
    msgList = []
    qResp = sqsclient.list_queues( QueueNamePrefix=sqsQueue )
    if "QueueUrls" in qResp:
      urlList = qResp["QueueUrls"]
      if len(urlList) == 1:
        sqsURL = urlList[0]
        msgList = self.receiveSQSMessages(sqsclient, sqsURL)
        if len(msgList) > 0:
          self.deleteSQSMessages(sqsclient, sqsURL, msgList)
      else:
        self.logger.warning("Unable to determine sqs queue with prefix: {0}".format(sqsQueue))
    return msgList


  '''
  Get the messages from the sqs queue
  '''
  def receiveSQSMessages(self, sqsclient, sqsURL):
    messageList = []
    lastMsg = False
    while lastMsg == False:
      msgResp = sqsclient.receive_message( QueueUrl=sqsURL, VisibilityTimeout=4 )
      if "Messages" in msgResp:
        sqsMsgList = msgResp["Messages"]
        if len(sqsMsgList) > 0:
          messageList = messageList + sqsMsgList
        else:
          lastMsg = True
      else:
        lastMsg = True

    return messageList


  '''
  Delete the messages that we have received from the SQS queue
  '''
  def deleteSQSMessages(self, sqsclient, sqsURL, msgList):
    for messageDict in msgList:
      if "ReceiptHandle" in messageDict:
        receiptHandle = messageDict["ReceiptHandle"]
        sqsclient.delete_message( QueueUrl=sqsURL, ReceiptHandle=receiptHandle)
        self.logger.info("receiptHandle: {0}".format(receiptHandle))





