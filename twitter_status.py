#!/usr/bin/env python3

# -*- coding: utf-8 -*-

# Based on https://github.com/bear/python-twitter/blob/master/examples/tweet.py

import configparser
import getopt
import os
import sys
import twitter
import re

def PrintUsageAndExit():
  print(USAGE)
  sys.exit(2)

def GetConsumerKeyEnv():
  return os.environ.get("TWEETUSERNAME", None)

def GetConsumerSecretEnv():
  return os.environ.get("TWEETPASSWORD", None)

def GetAccessKeyEnv():
  return os.environ.get("TWEETACCESSKEY", None)

def GetAccessSecretEnv():
  return os.environ.get("TWEETACCESSSECRET", None)

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetConsumerKey(self):
    return self._GetOption('consumer_key')

  def GetConsumerSecret(self):
    return self._GetOption('consumer_secret')

  def GetAccessKey(self):
    return self._GetOption('access_key')

  def GetAccessSecret(self):
    return self._GetOption('access_secret')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
      return None

  def _GetConfig(self):
    if not self._config:
      self._config = configparser.ConfigParser()
      self._config.read(os.path.expanduser('~/.tweetrc'))
    return self._config

def main():
  try:
    shortflags = 'h'
    longflags = ['help', 'consumer-key=', 'consumer-secret=', 
                 'access-key=', 'access-secret=', 'encoding=']
    opts, args = getopt.gnu_getopt(sys.argv[1:], shortflags, longflags)
  except getopt.GetoptError:
    PrintUsageAndExit()
  consumer_keyflag = None
  consumer_secretflag = None
  access_keyflag = None
  access_secretflag = None
  encoding = None
  for o, a in opts:
    if o in ("-h", "--help"):
      PrintUsageAndExit()
    if o in ("--consumer-key"):
      consumer_keyflag = a
    if o in ("--consumer-secret"):
      consumer_secretflag = a
    if o in ("--access-key"):
      access_keyflag = a
    if o in ("--access-secret"):
      access_secretflag = a
    if o in ("--encoding"):
      encoding = a
  rc = TweetRc()
  consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
  consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
  access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
  access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
  if not consumer_key or not consumer_secret or not access_key or not access_secret:
    PrintUsageAndExit()
  api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                    access_token_key=access_key, access_token_secret=access_secret,
                    input_encoding=encoding)
  status = api.GetHomeTimeline()[0]
  try:
     last_id = open("last_id.txt", "r").read()
  except IOError:
     last_id = "abracadabrao"
  if last_id == status.id_str:
     sys.exit(0)
  print('id="%s", last="%s"' % (status.id_str, last_id), file=sys.stderr)
  open("last_id.txt", "w").write(status.id_str)
  text = status.retweeted_status and ("RT " + status.retweeted_status.text) or status.text
  text = re.sub("http[^ ]+", "url", text)
  print(text)

if __name__ == "__main__":
  main()
