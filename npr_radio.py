import time
import vlc
import npr
import sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

class NPRadio():
	def __init__(self):
		self.initialize()
		self.checkAlarm() # -- check if alarm is active on initialization

	def play(self):
		self.player.play()

	def stop(self):
		self.player.stop()

	def checkAlarm(self):
		'''Check the alarm state'''
		self.alarm = GPIO.input(27)
		if self.alarm == 1:
			self.player.stop()
			sys.exit()

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
	# -- initialize NPR
	player = NPRadio()
	player.play()

	while True:
		# -- check button state
		if GPIO.input(27):
			player.stop()
			sys.exit()

		time.sleep(0.1)

