import os, sys, time
import requests

class Radio(object):
	'''Audio from Radio'''
	def __init__(self, station):
		self.status = 'ready'
		self.station = station

		self._exec_command("service mpd start")
		self._exec_command("mpc clear")

		stream = self._fetch_stream(station)

		self._exec_command("mpc add {}".format(stream))		

	def play(self, duration=10):
		'''Start Playing station'''
		self.status = 'playing'
		self._exec_command("mpc play")

	def stop(self):
		''' Stop playing the station'''
		self._exec_command("mpc stop")
		self.status = 'ready'

	def _exec_command(self, cmd):
		result = ""
		p = os.popen(cmd)
		for line in p.readline().split('\n'):
			result = result + line
		
		return result	

	def _fetch_stream(self, url):
		#what we're looking for
		search='File1='
		r = requests.get(url)
		if r.status_code == 200:
			print r.text
			for line in r.text.splitlines():
				if search in line:
					return line.lstrip(search)	

if __name__ == '__main__':
	stations = {
		'WNYC'      : 'http://www.wnyc.org/stream/wnyc-fm939/aac.pls',
	}	

	radio = Radio(stations['WNYC'])
	print "Status: {}".format(radio.status)

	radio.play()
	time.sleep(30)
	radio.stop()