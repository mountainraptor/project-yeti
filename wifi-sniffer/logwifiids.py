#!/usr/bin/python

import os, sys, argparse, subprocess, time, sqlite3
import signal

HASH_MAP_SIZE = 512
HASH_MAP_STALE_TIME = 15
p = None

class MacEntry(object):
   def __init__(self, epoch, mac, snr, ssid):
      self.epoch = epoch
      self.mac = mac
      self.snr = snr
      self.count = 1
      self.lastEpoch = epoch
      if (ssid != None):
         self.ssids = ssid
      else:
         self.ssids = None

   def __eq__(self, other):
      try:
         return (self.mac == other.mac)
      except:
         return False

   def isNextValid(self, nextEntry):
      return True
   
   def addNewEntry(self, nextEntry):
      if (self.mac != nextEntry.mac):
         print 'Error does not match'
         return None
      if self.isNextValid(nextEntry) == False:
         print 'Invalid entry'
         if (self.errors > nextEntry.errors):
            print 'Using newer entry with less errors'
            self.count = 1
            self = nextEntry
            print self
            print nextEntry
         return None
      self.count += 1
      self.lastEpoch = nextEntry.epoch
      self.snr = max(self.snr, nextEntry.snr)
      if (nextEntry.ssids != None):
         if (self.ssids == None):
            self.ssids = nextEntry.ssids
         elif (self.ssids.find(nextEntry.ssids) < 0):
            self.ssids = self.ssids + ',' + nextEntry.ssids
      return self.count
   
   def __repr__(self):
      return 'MAC %s, count = %d, ssids = %s' % (hex(self.mac), self.count, self.ssids)

def textToMacEntry(line):
   ssid = None
   linefields = line.split(' ')
   if (len(linefields) < 10):
      return None
   ts = int(linefields[0].split('.')[0])
   decodingSSID = False
   for field in linefields:
      if (decodingSSID):
         ssid += field
         if (field.endswith(')')):
            ssid = ssid[:-1]
            decodingSSID = False
      elif (field.endswith('dB')):
         snr = int(field[:-2])
      elif (field.startswith('SA:')):
         mactxt = field[3:].replace(':', '')
         mac = int(mactxt, 16)
      elif (field.startswith('(')):
         ssid = field[1:]
         if (field.endswith(')')):
            ssid = ssid[:-1]
            if (len(ssid) == 0):
               ssid = None
            decodingSSID = False
         else:
            decodingSSID = True
   
   try:
      return MacEntry(ts, mac, snr, ssid)
   except Exception as   e:
      return None

def flushAllHashMap(dB, hashMap):
   for i in range(0, len(hashMap)):
      if (hashMap[i] != None):
         dB.addEntryIfValid(hashMap[i])
         hashMap[i] = None
   dB.commitOutstandingEntries()

def cleanupHashMap(dB, hashMap):
   curTime = int(time.time())
   for i in range(0, len(hashMap)):
      if (hashMap[i] != None):
         if (isEntryStale(hashMap[i])):
            dB.addEntryIfValid(hashMap[i])
            hashMap[i] = None
   dB.commitOutstandingEntries()

def isEntryStale(entry, curTime=None):
   if (curTime == None):
      curTime = int(time.time())
   return (entry.lastEpoch + HASH_MAP_STALE_TIME < curTime)

def hashFunction(entry):
   return entry.mac % HASH_MAP_SIZE

def runTcpDumpTest(dB):
   hashMap = [None] * HASH_MAP_SIZE
   tf = file('./epoch-sample.out', 'r')
   while 1:
      entry = tf.readline()
      print entry
      le = textToMacEntry(entry)
      if (le == None):
         print 'Error decoding line ' + entry
         flushAllHashMap(dB, hashMap)
         sys.exit(1)
      cleanupHashMap(dB, hashMap)
      hashIndex = hashFunction(le)
      if (hashMap[hashIndex] != None):
         if (hashMap[hashIndex] == le):
            hashMap[hashIndex].addNewEntry(le)
         else:
            print 'hash collision ' + str(hashMap[hashIndex]) + ' ' + str(le)
            dB.addSingleEntryIfValid(hashMap[hashIndex])
            hashMap[hashIndex] = le
      else:
         hashMap[hashIndex] = le
         
      print hashMap[hashIndex]
   print p.stdout.readlines()

def preexec_function():
    # Ignore the SIGINT signal by setting the handler to the standard
    # signal handler SIG_IGN.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def runTcpDump(dB):
   global p
   hashMap = [None] * HASH_MAP_SIZE
   print 'Starting capture'
   p = subprocess.Popen(['tcpdump', '-i', 'wlan0', '-s0', '-tt', '-l', '-nne', 'wlan', 'type', 'mgt', 'subtype', 'probe-req'], stdout=subprocess.PIPE, preexec_fn = preexec_function)
   while p.poll() is None:
      cleanupHashMap(dB, hashMap)
      entry = p.stdout.readline()
      if (len(entry) == 0):
         continue
      le = textToMacEntry(entry)
      if (le == None):
         print 'Error decoding line ' + entry
         continue
      hashIndex = hashFunction(le)
      if (hashMap[hashIndex] != None):
         if (hashMap[hashIndex] == le):
            hashMap[hashIndex].addNewEntry(le)
         else:
            print 'hash collision ' + str(hashMap[hashIndex]) + ' ' + str(le)
            dB.addSingleEntryIfValid(hashMap[hashIndex])
            hashMap[hashIndex] = le
      else:
         hashMap[hashIndex] = le
      print hashMap[hashIndex]
   print 'Flushing all hashmap entries and exiting'
   flushAllHashMap(dB, hashMap)

class macDb(object):
   def __init__(self, dBFile):
      self.conn = sqlite3.connect(dBFile)
      self.cursor = self.conn.cursor()
      #check to see if table is created
      try:
         self.cursor.execute('SELECT * FROM macTable LIMIT 1')
      except Exception as e:
         self.cursor.execute('CREATE TABLE macTable(addr INT NOT NULL, epoch INT NOT NULL, errors INT NOT NULL, count INT NOT NULL, duration INT NOT NULL, snr INT NOT NULL, extrainfo STRING)')
         self.conn.commit()
      
   def addSingleEntryIfValid(self, entry):
      self.addEntryIfValid(entry)
      self.commitOutstandingEntries()
      
   def addEntryIfValid(self, entry):
      if (True): # For wifi entries are awlways considered valid
         print 'Adding entry for ' + str(entry)
         duration = entry.lastEpoch - entry.epoch
         self.cursor.execute('INSERT INTO macTable VALUES(?, ?, ?, ?, ?, ?, ?)', (entry.mac, entry.epoch, 0, entry.count, duration, entry.snr, entry.ssids))
      
   def commitOutstandingEntries(self):
      self.conn.commit()

def signal_handler(signal, frame):
   print('You pressed Ctrl+C!')
   if (p != None):
      p.terminate()
   else:
      sys.exit(0)

def main():
   signal.signal(signal.SIGINT, signal_handler)
   parser = argparse.ArgumentParser(description='Log WIFI MAC addresses to sqlite dB using tcpdump')
   parser.add_argument('-d', '--database', help='SQLite dB file to store data in', default='wifi-macs.sqlite')
   
   config = parser.parse_args()
   
   dB = macDb(config.database)
   
   runTcpDump(dB)


if __name__ == "__main__":
    main()
