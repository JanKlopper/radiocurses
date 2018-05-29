#!/usr/bin/python2.7
"""A python curses di.fm stream player for low mem systems"""
__author__ = ('Jan Klopper <jan@underdark.nl>',
              'Gerjan Klinkhamer gerjan@underdark.nl')
__version__ = 0.1

import curses
from cursesmenu import *
from cursesmenu.items import *

import os
import requests
import simplejson
import time

DICHANNELS = ['http://listen.di.fm/premium_high.json',
              'http://listen.radiotunes.com/premium_high.json',
              'http://listen.rockradio.com/premium_high.json',
              'http://listen.jazzradio.com/premium_high.json',
              'http://listen.classicalradio.com/premium_high.json']
DIURLPREMIUM = 'http://prem4.di.fm:80/%s_hi?%s'
PLAYER = 'mplayer -nolirc -nojoystick -quiet %s'
CODE = ''  # fill this with your premium code
MAXCACHEAGE = (60*60*24*7)  # in seconds
PAGEOFFSET = 15
CONFIGFILE = "~/.radiocurses"

class MyCursesMenu(CursesMenu):

  def process_user_input(self):
    """
    Gets the next single character and decides what to do with it
    """
    user_input = self.get_input()

    go_to_max = ord("9") if len(self.items) >= 9 else ord(str(len(self.items)))

    if ord('1') <= user_input <= go_to_max:
      self.go_to(user_input - ord('0') - 1)
    elif user_input == curses.KEY_PPAGE:
      for i in xrange(0, PAGEOFFSET):
        self.go_up()
    elif user_input == curses.KEY_NPAGE:
      for i in xrange(0, PAGEOFFSET):
        self.go_down()
    elif user_input == curses.KEY_DOWN:
      self.go_down()
    elif user_input == curses.KEY_UP:
      self.go_up()
    elif user_input == ord("\n"):
      self.select()
    elif user_input == ord("q"):
      self.exit()
    return user_input

class radiocurses(object):

  def __init__(self, options={}):
    self.options = options
    self.dichannels = []
    self.ReadDiChannels()
    self.menu = None

    if self.options.premium:
      self.SaveCode(self.options.premium)
      self.code = self.options.premium
    else:
      configcode = self.ReadCode()
      if configcode:
        self.code = configcode
      else:
        self.code = CODE
    self.Populate()

  def Populate(self):
    """Actually populates the menu"""
    self.menu = MyCursesMenu("Radio Curses by Frack.nl", "Select a channel:")
    self.menu.append_item(FunctionItem("Refresh DI.fm cache", self.fetchDiFM))

    for channel in self.dichannels:
      url = "%s" % (PLAYER % (DIURLPREMIUM % (channel[1], self.code)))
      self.menu.append_item(CommandItem((channel[0] + '\n').encode('utf-8'), url))
    self.menu.show()

  def ReadCode(self):
    """Read the users premium code to a config file"""
    try:
      with open(os.path.expanduser(CONFIGFILE), "r") as infile:
        return infile.read().strip()
    except IOError:
      return False

  def SaveCode(self, code):
    """Store the users premium code to a config file"""
    try:
      with open(os.path.expanduser(CONFIGFILE), "w") as outfile:
        outfile.write(code)
        print("Premium key stored for future use.")
    except IOError:
      print("Could not write premium key to configfile: %r" % CONFIGFILE)

  def fetchDiFM(self):
    print 'Refreshing DI.fm channel cache...'
    channels = []
    for url in DICHANNELS:
      data = requests.get(url)
      try:
        data.raise_for_status()
        data = simplejson.loads(data.text)
        print 'Succesfully loaded channels from %s' % url
        for channel in data:
          channels.append((channel['name'], channel['key']))

      except Exception as error:
        print error

    self.dichannels = channels
    self.StoreDiChannels(channels)

  def StoreDiChannels(self, channels):
    dicache = open('di.json', 'w')
    dicache.write(simplejson.dumps(channels))
    dicache.close()

  def ReadDiChannels(self):
    try:
      if (time.time() - os.stat('di.json').st_mtime) > MAXCACHEAGE:
        return self.fetchDiFM()
      self.dichannels = simplejson.loads(open('di.json').read())
    except (IOError, OSError):
      self.fetchDiFM()

if __name__ == '__main__':
  import optparse
  parser = optparse.OptionParser()
  parser.add_option('-p', action="store", dest="premium", default=None)
  options, remainder = parser.parse_args()
  radio = radiocurses(options)
