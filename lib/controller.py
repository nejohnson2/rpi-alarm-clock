'''This is a module that controls
various parameters of the clock
radio'''

import alsaaudio

class Controller(object):
	def __init__(self):
		self.mixer = alsaaudio.Mixer('PCM')

	def set_volume(self, volume):
		self.mixer.setvolume(volume)

	def get_volume(self):
		return self.mixer.getvolume()

if __name__ == '__main__':
	controller = Controller()
	print controller.get_volume()
	controller.set_volume(70)
	print controller.get_volume()


