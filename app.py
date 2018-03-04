import os, sys, time
import json
import requests
import threading
import multiprocessing as mp
from tornado import gen
from tornado import websocket, web, ioloop	
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import PeriodicCallback

from clock import Clock
from controller import Controller
from scheduler import Scheduler

# -- For Websockets
cl = []

# Weather Underground API
apikey = '1473eef1c8584998'
features = ['conditions','astronomy']
pws_id = 'KNYASTOR5'
weather_url = 'http://api.wunderground.com/api/{}/{}/q/pws:{}.json'

class IndexHandler(web.RequestHandler):
	'''Handle requests on / '''
	def get(self):
		self.render("index.html")


class WeatherHandler(web.RequestHandler):
	@gen.coroutine
	def get(self):
		# current = time.strftime("%H:%M:%S")		
		url = [weather_url.format(apikey, features[0], pws_id), 
				weather_url.format(apikey, features[1], pws_id)]

		weather, astronomy = yield [self.fetch_weather(url[0]), self.fetch_weather(url[1])]
		print weather['current_observation']['temp_c']
		print astronomy['moon_phase']['sunrise']
		print astronomy['moon_phase']['sunset']
		
	@gen.coroutine
	def fetch_weather(self, url):
		http_client = AsyncHTTPClient()
		response = yield http_client.fetch(url)
		raise gen.Return(json.loads(response.body))

class WebSocketHandler(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True

	def open(self):
		'''Send current values once a 
		socket has been opened'''
		alarm = self.settings['alarm']
		controller = self.settings['controller']

		alarms = alarm.get_current_alarms()
		vol = controller.get_volume()
		message={'alarm':alarms[0], 'volume':vol[0]}

		if self not in cl:
			cl.append(self)

		self.write_message(message)

	def on_close(self):
		if self in cl:
			cl.remove(self)

	def on_message(self, message):
		'''Set alarm clock parameters
		when recieved from client'''
		print "Client received message: %s" %(message)
		message = json.loads(message)
		
		if message['type'] == 'alarm':
			hour, minute = message['value'].split(':')
			print "Alarm set to : " + message['value']

			# -- Get alarm object
			alarm = self.settings['alarm']
			alarm.schedule_alarm(hour, minute)

		elif message['type'] == 'volume':
			# -- Get controller object
			controller = self.settings['controller']
			controller.set_volume(int(message['value']))


def main():
	# -- Launch the clock in a seperate process
	clock = Clock()
	clock.start()

	settings = {
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"debug" : True,
		"alarm" : Scheduler(),
		"controller" : Controller(),
	}
	
	app = web.Application(
		[
			(r'/', IndexHandler),
			(r'/ws', WebSocketHandler),
			(r'/weather', WeatherHandler),
		], **settings
	)

	port = int(os.environ.get("PORT", 5000))
	print "Listening on port: %s"%(port)
	app.listen(port)
	ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()
