import os
import time
import json
import requests
import logging
import subprocess
from tornado import gen
from tornado import websocket, web, ioloop	
from tornado.httpclient import AsyncHTTPClient

from lib import Clock, Controller, Scheduler

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

		# -- get any current states
		alarms = alarm.get_current_alarms()
		vol = controller.get_volume()
		
		if alarms:
			message={'alarm':alarms[0], 'volume':vol[0]}
		else:
			message={'alarm':'None', 'volume':vol[0]}

		# -- get clients
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
		
		# -- Schedule new alarm
		if message['type'] == 'alarm':
			hour, minute = message['value'].split(':')
			print "Alarm set to : " + message['value']

			# -- Get alarm object
			alarm = self.settings['alarm']
			alarm.schedule_alarm(hour, minute)

		# -- Set new volume
		elif message['type'] == 'volume':
			# -- Get controller object
			controller = self.settings['controller']
			controller.set_volume(int(message['value']))

		# -- turn off an live radio stream
		elif message['type'] == 'off':
			try:
				# -- get radio process
				cmd = 'ps ax | grep npr_radio | awk \'{if ($5 == \"python\") print $1}\''
				pid = subprocess.check_output(cmd, shell=True)

				# -- kill process
				subprocess.call('sudo kill {}'.format(pid), shell=True)
			except:
				pass
				
		# -- Remove any existing alarms
		elif message['type'] == 'clear':
			# -- get objects
			alarm = self.settings['alarm']
			controller = self.settings['controller']
			
			# -- clear an alarm
			alarm.clear_alarm()
			vol = controller.get_volume()
			
			# -- send new data to user
			message={'alarm':'None', 'volume':vol[0]}

			if self not in cl:
				cl.append(self)

			self.write_message(message)			


def main():
	# -- Launch the clock in a seperate process
	# clock = Clock()
	# clock.start()

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
