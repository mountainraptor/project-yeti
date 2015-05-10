#!/usr/bin/python

import os, sys, argparse, subprocess, time, sqlite3

HASH_MAP_SIZE = 512
HASH_MAP_STALE_TIME = 15

lapDb = None

class LapEntry(object):
   def __init__(self, epoch, channel, lap, errors, clk100ns, clk1, signal, noise, snr):
      self.epoch = epoch
      self.channel = channel
      self.lap = lap
      self.errors = errors
      self.clk100ns = clk100ns
      self.clk1 = clk1
      self.signal = signal
      self.noise = noise
      self.snr = snr
      self.count = 1
      self.lastEpoch = epoch

   def __eq__(self, other):
      try:
         return (self.lap == other.lap)
      except:
         return False

   def isNextValid(self, nextLapEntry):
      try:
         if (self.lap == nextLapEntry.lap and self.clk100ns < nextLapEntry.clk100ns and self.clk1 < nextLapEntry.clk1):
            return True
         else:
            return False
      except:
         print 'Error comparing next entry'
         return False
   
   def addNewEntry(self, nextLapEntry):
      if (self.lap != nextLapEntry.lap):
         print 'Error does not match'
         return None
      if self.isNextValid(nextLapEntry) == False:
         print 'Invalid entry'
         if (self.errors > nextLapEntry.errors):
            print 'Using newer entry with less errors'
            self.count = 1
            self = nextLapEntry
            print self
            print nextLapEntry
         return None
      self.count += 1
      self.lastEpoch = nextLapEntry.epoch
      self.errors = min(self.errors, nextLapEntry.errors)
      self.clk1 = max(self.clk1, nextLapEntry.clk1)
      self.clk100ns = max(self.clk100ns, nextLapEntry.clk100ns)
      self.snr = max(self.snr, nextLapEntry.snr)
      self.signal = max(self.signal, nextLapEntry.signal)
      self.noise = max(self.noise, nextLapEntry.noise)
      return self.count
   
   def __repr__(self):
      return 'LAP %s, errors = %d, ch = %d, count = %d' % (hex(self.lap), self.errors, self.channel, self.count)

def textToLapEntry(line):
   s = line.replace('= ', '=').split(' ')
   if len(s) != 9:
      print 'Error parsing line ' + line
      return None
   #TODO try:
   time = int(s[0].split('=')[1])
   channel = int(s[1].split('=')[1])
   lap = int(s[2].split('=')[1], 16)
   errors = int(s[3].split('=')[1])
   clk100ns = int(s[4].split('=')[1])
   clk1 = int(s[5].split('=')[1])
   signal = int(s[6].split('=')[1])
   noise = int(s[7].split('=')[1])
   snr = int(s[8].split('=')[1])
   return LapEntry(time, channel, lap, errors, clk100ns, clk1, signal, noise, snr)


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

def hashFunction(lapEntry):
   return lapEntry.lap % HASH_MAP_SIZE

def runUbertoothRx(dB, maxErrors):
   hashMap = [None] * HASH_MAP_SIZE
   p = subprocess.Popen(['unbuffer', 'ubertooth-rx', '-e', str(maxErrors), '-s'], stdout=subprocess.PIPE)
   while p.poll() is None:
      entry = p.stdout.readline()
      le = textToLapEntry(entry)
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

class lapDb(object):
   def __init__(self, dBFile):
      self.conn = sqlite3.connect(dBFile)
      self.cursor = self.conn.cursor()
      #check to see if table is created
      try:
         self.cursor.execute('SELECT * FROM lapTable LIMIT 1')
      except Exception as e:
         self.cursor.execute('CREATE TABLE lapTable(addr INT NOT NULL, epoch INT NOT NULL, errors INT NOT NULL, count INT NOT NULL, duration INT NOT NULL, snr INT NOT NULL)')
         self.conn.commit()
      
   def addSingleEntryIfValid(self, entry):
      self.addEntryIfValid(entry)
      self.commitOutstandingEntries()
      
   def addEntryIfValid(self, entry):
      if (entry.count > 1 or entry.errors == 0):
         print 'Adding entry for ' + str(entry)
         duration = entry.lastEpoch - entry.epoch
         self.cursor.execute('INSERT INTO lapTable VALUES(?, ?, ?, ?, ?, ?)', (entry.lap, entry.epoch, entry.errors, entry.count, duration, entry.snr))
      
   def commitOutstandingEntries(self):
      self.conn.commit()

def main():
   parser = argparse.ArgumentParser(description='Log bluetooth LAPs to sqlite dB using ubertooth-rx')
   parser.add_argument('-d', '--database', help='SQLite dB file to store LAPs in', default='bt-laps.sqlite')
   parser.add_argument('-e', '--max-errors', help='Max number of errors in decoded packet for ubertooth', default=2)
   
   config = parser.parse_args()
   
   dB = lapDb(config.database)
   
   runUbertoothRx(dB, config.max_errors)


if __name__ == "__main__":
    main()
