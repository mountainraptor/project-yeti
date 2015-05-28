#!/usr/bin/python

import os, sys, argparse, subprocess, time, sqlite3, md5
import signal

p = None
STORE_EXTRA_INFO=False
HASH_ADDRESS=True

class MacEntry(object):
   def __init__(self, epoch, mac, snr, ssid):
      self.epoch = epoch
      if (HASH_ADDRESS):
         self.addr = buffer(md5.new(mac).digest())
      else:
         self.addr = buffer(mac)
      self.snr = snr
      self.lastEpoch = epoch
      if (ssid != None and STORE_EXTRA_INFO):
         self.ssids = ssid
      else:
         self.ssids = None

   def __eq__(self, other):
      try:
         return (self.addr == other.addr)
      except:
         return False
   
   
   def __repr__(self):
      return 'AddrHash %s, ssid = %s, snr = %d' % (''.join('{:02x}'.format(ord(x)) for x in str(self.addr)), self.ssids, self.snr)

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
         mac = field[3:].replace(':', '')
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

def runTcpDumpTest(dB):
   tf = file('./epoch-sample.out', 'r')
   while 1:
      entry = tf.readline()
      #print entry
      le = textToMacEntry(entry)
      if (le == None):
         print 'Error decoding line ' + entry
         dB.commitOutstandingEntries()
         sys.exit(1)
      print le
      dB.addEntryIfValid(le)

def preexec_function():
    # Ignore the SIGINT signal by setting the handler to the standard
    # signal handler SIG_IGN.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def runTcpDump(dB):
   global p
   print 'Starting capture'
   p = subprocess.Popen(['tcpdump', '-i', 'wlan0', '-s0', '-tt', '-l', '-nne', 'wlan', 'type', 'mgt', 'subtype', 'probe-req'], stdout=subprocess.PIPE, preexec_fn = preexec_function)
   while p.poll() is None:
      entry = p.stdout.readline()
      if (len(entry) == 0):
         continue
      le = textToMacEntry(entry)
      if (le == None):
         print 'Error decoding line ' + entry
         continue
      print le
      dB.addEntry(le)      
      dB.commitTimer()
   
   dB.commitOutstandingEntries()

class macDb(object):
   FLUSH_INTERVAL = 10
   def __init__(self, dBFile):
      self.lastFlush = None
      self.conn = sqlite3.connect(dBFile)
      self.cursor = self.conn.cursor()
      #check to see if table is created
      try:
         self.cursor.execute('SELECT * FROM macTable LIMIT 1')
      except Exception as e:
         self.cursor.execute('CREATE TABLE macTable(addrHash BLOB NOT NULL, epoch INT NOT NULL, errors INT NOT NULL, snr INT NOT NULL, extrainfo STRING)')
         self.conn.commit()
      
   def addSingleEntry(self, entry):
      self.addEntryIfValid(entry)
      self.commitOutstandingEntries()
      
   def addEntry(self, entry):
      self.cursor.execute('INSERT INTO macTable VALUES(?, ?, ?, ?, ?)', (entry.addr, entry.epoch, 0, entry.snr, entry.ssids))
      if (self.lastFlush == None):
         self.lastFlush = time.time()
      
   def commitOutstandingEntries(self):
      print 'Flushing database entries'
      self.conn.commit()
      self.lastFlush = None
      
   def commitTimer(self):
      if (self.lastFlush != None):
         if (time.time() > self.lastFlush + macDb.FLUSH_INTERVAL):
            self.commitOutstandingEntries()

def signal_handler(signal, frame):
   print('You pressed Ctrl+C!')
   if (p != None):
      p.terminate()
   else:
      sys.exit(0)

def main():
   signal.signal(signal.SIGINT, signal_handler)
   parser = argparse.ArgumentParser(description='Log WIFI MAC addresses to sqlite dB using tcpdump')
   parser.add_argument('-d', '--database-folder', help='SQLite dB file to store data in', default='./')
   
   config = parser.parse_args()
   
   num = 0
   while True:
      dbpath = '%s/wifi-macs_%04d.sqlite' % (config.database_folder, num)
      num += 1
      if (not os.path.isfile(dbpath)):
         break
      
   print 'using db ' + dbpath
      
   dB = macDb(dbpath)
   
   runTcpDump(dB)


if __name__ == "__main__":
    main()
