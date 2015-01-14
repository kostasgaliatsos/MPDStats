#!/usr/bin/python

from mpd import MPDClient
from threading import Thread
from threading import Timer
import sqlite3
import time
import sys

class stats(Thread):

    INTERVAL = 1
    olddata = None
    LOGFILE =  "./stats.log"

    def __init__(self):
        super(stats, self).__init__()
        self._client = MPDClient()
        self._client.connect(self.HOST, self.PORT)
        self.db = dbconn()

    def run(self):
        while True:
            stats = self._getstats()
            if stats:
                stats = self._validate(stats)
                state = self._client.status()['state']
                if stats != self.olddata and state == 'play':
                    length = self._length()/2
                    t = Timer(length, self.db.insertstats, [stats])
                    t.start()
                    self.olddata = stats
            time.sleep(self.INTERVAL)

    def _getstats(self):
        currsong = self._client.currentsong()
        if currsong != {}:
            try:
                stats = [currsong['artist'], currsong['album'], currsong['title'], currsong['genre'], currsong['time']]        
                return stats
            except Exception as e:
                localtime = time.asctime( time.localtime(time.time()) )
                file = open(self.LOGFILE, 'a')
                file.write(localtime + ': ' + e.__str__()+ '\n')
        return None

    def _length(self):
        currsong = self._client.currentsong()
        length=float(currsong['time'])
        return length

    def _validate(self, data):
        for i in range(len(data)):
            if "'" in data[i]:
                data[i] = data[i].replace("'", "")
        return data

class dbconn:
    SQLFILE = "./stats.db"
    LOGFILE =  "./stats.log"

    #def __init__(self):

    def insertstats(self, stats):
	try:
		self.conn = sqlite3.connect(self.SQLFILE)
		self.cursor = self.conn.cursor()
	except sqlite3.Error as e:
                localtime = time.asctime( time.localtime(time.time()) )
		file = open(self.LOGFILE, 'a')
		file.write(localtime, ':', e.__str__(), '\n')
        sql = 'INSERT INTO listening(artist, album, title, genre, length, listenedon) VALUES ('
        for i in stats:
            sql += "'" + i.__str__() + "',"
        sql += 'datetime());'
	try:
        	self.cursor.execute(sql)
        	self.conn.commit()
	except sqlite3.Error as e:
		file = open(self.LOGFILE, 'a')
                localtime = time.asctime( time.localtime(time.time()) )
                file.write(localtime, ':', e.__str__(), '\n')

def main():
    s = stats()
    s.start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
