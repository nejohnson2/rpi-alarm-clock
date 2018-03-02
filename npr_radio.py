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
			# npr.login()
			station = npr.Station('WNYC')
			url = station.live()
		except Exception as e:
			print 'Unable to get NPR'
			print e

		try:
			instance = vlc.Instance()
			self.player = instance.media_player_new()
			media = instance.media_new(url)

			self.player.set_media(media)
		except Exception as e:
			print 'Failed to launch VLC player'
			print e


if __name__ == '__main__':
	player = NPRadio()
	player.play()
	time.sleep(10)
	player.stop()