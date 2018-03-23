import os, sys, time
import requests
import datetime
from multiprocessing import Process

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_ILI9341 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

class Clock(Process):
	def __init__(self):
		super(Clock, self).__init__()
		self.disp = TFT.ILI9341(17, rst=23, spi=SPI.SpiDev(0, 0, max_speed_hz=64000000))
		self.font = ImageFont.truetype('fonts/OpenSans-Bold.ttf', 110)
		self.disp.begin()
		self.disp.clear()

	def run(self):

		last_displayed_time = None

		while True:

			current_time = datetime.datetime.now().time()

			if (last_displayed_time is None) or (current_time.second != last_displayed_time.second):
				self._update_screen()
				last_displayed_time = current_time

			time.sleep(.1)

	def _update_screen(self):		
		# -- Get curent time round to nearest minute
		tm = datetime.datetime.now()
		tm = tm - datetime.timedelta(minutes=tm.minute % 1,
									 seconds=tm.second,
									 microseconds=tm.microsecond)		
		# -- Draw currecnt time to screen
		self.disp.clear()
		self._draw_rotated_text(tm.strftime('%-I:%M'), 90)
		self.disp.display()

	def _draw_rotated_text(self, text, angle, fill=(255,255,255)):
		
		# Get rendered font width and height.
		draw = ImageDraw.Draw(self.disp.buffer)
		width, height = draw.textsize(text, font=self.font)
		
		# Create a new image with transparent background to store the text.
		textimage = Image.new('RGBA', (width, height), (0,0,0,0))
		# Render the text.
		textdraw = ImageDraw.Draw(textimage)
		textdraw.text((0,0), text, font=self.font, fill=fill)
		# Rotate the text image.
		rotated = textimage.rotate(angle, expand=1)
		# Paste the text into the image, using it as a mask for transparency.
		self.disp.buffer.paste(rotated, ((200-height)/2,(320-width)/2), rotated)



if __name__ == '__main__':
	c = Clock()
	c.start()
	time.sleep(10)
	c.join()