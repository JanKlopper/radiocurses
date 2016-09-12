#!/usr/bin/python2.7
"""A python curses di.fm stream player for low mem systems"""
__author__ = 'Jan Klopper (jan@underdark.nl)'
__version__ = 0.1

from cursesmenu import *
from cursesmenu.items import *

import os
import requests
import simplejson
import time

DICHANNELS = ['http://www.di.fm/webplayer3/config',
              'http://www.rockradio.com/webplayer3/config',
              'http://www.jazzradio.com/webplayer3/config',
              'http://www.radiotunes.com/webplayer3/config']
DIURLPREMIUM = 'http://prem2.di.fm:80/%s_hi?%s'
PLAYER = 'mplayer %s'
CODE = '' # fill this with your premium code
MAXCACHEAGE = (60*60*24*7) # in seconds

class radiocurses(object):

  def __init__(self, options={}):
    self.options = options
    self.dichannels = []
    self.ReadDiChannels()

    menu = CursesMenu("Radio Curses by Frack.nl", "Select a channel:")
    menu.append_item(FunctionItem("Refresh DI.fm cache", self.fetchDiFM))


    code = (self.options.premium if self.options.premium else CODE)
    for channel in self.dichannels:
      url = "%s" % (PLAYER % (DIURLPREMIUM % (channel[1], code)))
      menu.append_item(CommandItem(channel[0].encode('utf-8'), url))
    menu.show()

  def fetchDiFM(self):
    print 'Refreshing DI.fm channel cache'
    channels = []
    for url in DICHANNELS:
      data = requests.get(url)
      data = simplejson.loads(data.text)
      for channel in data['WP']['channels']:
        channels.append((channel['name'], channel['key']))
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
