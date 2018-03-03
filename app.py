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
from scheduler import Scheduler

# Weather Underground API
apikey = '1473eef1c8584998'
features = ['conditions','astronomy']
pws_id = 'KNYASTOR5'
weather_url = 'http://api.wunderground.com/api/{}/{}/q/pws:{}.json'

class IndexHandler(web.RequestHandler):
	'''Handle requests on / '''
	def get(self):
		alarm = self.settings['alarm']
		alarms = alarm.get_current_alarms()

		if alarms:
			self.render("index.html", alarm=alarms[0])
		else:
			self.render("index.html", alarm='None')

class SetAlarmHandler(web.RequestHandler):
	def post(self):
		time = self.get_argument("time", "")
		hour, minute = time.split(':')
		print "Alarm set to : " + time

		alarm = self.settings['alarm']
		alarm.schedule_alarm(hour, minute)

		self.redirect('/')


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


def main():
	# -- Launch the clock in a seperate process
	clock = Clock()
	clock.start()

	settings = {
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"debug" : True,
		"alarm" : Scheduler()
	}
	
	app = web.Application(
		[
			(r'/', IndexHandler),
			(r'/set_alarm', SetAlarmHandler),
			(r'/weather', WeatherHandler),
		], **settings
	)

	port = int(os.environ.get("PORT", 5000))
	print "Listening on port: %s"%(port)
	app.listen(port)
	ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()
