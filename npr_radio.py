import time
import vlc
import npr

class NPRadio():
	def __init__(self):
		self.initialize()

	def play(self):
		self.player.play()

	def stop(self):
		self.player.stop()

	def initialize(self):
		try:
			station = npr.Station(554)
		except Exception as e:
			print 'Unable to get NPR'
			print e

		try:
			self.player = vlc.MediaPlayer(station.stream)

		except Exception as e:
			print 'Failed to setup VLC player'
			print e


if __name__ == '__main__':
	player = NPRadio()
	player.play()
	time.sleep(10)
	player.stop()